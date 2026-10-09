"""
Options Dashboard v2 — Stage 8
Crypto prices converted to USD. Tabs + colored Calls/Puts.
"""
from dash import (
    Dash, html, dcc, callback, ctx,
    Input, Output, State, ALL as dash_all, no_update,
)
import dash_ag_grid as dag
import plotly.graph_objects as go
import requests
import urllib3
import yfinance as yf
import time
from curl_cffi import requests as curl_requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


DERIBIT = "https://www.deribit.com/api/v2"

BG = "#0e1117"
PANEL = "#161b22"
BORDER = "#30363d"
TEXT = "#e6edf3"
MUTED = "#8b949e"
PROFIT = "#2ecc71"
LOSS = "#e74c3c"
STRIKE = "#f39c12"
SPOT = "#58a6ff"
ACCENT = "#1f6feb"
RED = "#da3633"

CALL_COLOR = "#2ecc71"
PUT_COLOR = "#e74c3c"

CRYPTO_SYMBOLS = {"BTC", "ETH"}

_stock_session = curl_requests.Session(impersonate="chrome")
_stock_session.verify = False


# ---------- Cache ----------
_cache = {}
CACHE_TTL = 300


def cache_get(key):
    entry = _cache.get(key)
    if entry is None:
        return None
    value, expires = entry
    if time.time() > expires:
        del _cache[key]
        return None
    return value


def cache_set(key, value, ttl=CACHE_TTL):
    _cache[key] = (value, time.time() + ttl)


def http_get(url, params=None, timeout=15):
    try:
        return requests.get(url, params=params, timeout=timeout)
    except requests.exceptions.SSLError:
        return requests.get(url, params=params, timeout=timeout, verify=False)


# ---------- Crypto ----------
def get_crypto_expiries(currency="BTC"):
    key = f"expiries:{currency}"
    cached = cache_get(key)
    if cached is not None:
        return cached

    url = f"{DERIBIT}/public/get_instruments?currency={currency}&kind=option&expired=false"
    r = http_get(url)
    data = r.json().get("result", [])

    counts = {}
    labels = {}
    for i in data:
        if i.get("is_expired"):
            continue
        ts = i.get("expiration_timestamp")
        if ts:
            counts[ts] = counts.get(ts, 0) + 1
            labels[ts] = i["instrument_name"].split("-")[1]

    good = [(ts, labels[ts]) for ts, c in counts.items() if c >= 20]
    good.sort()
    cache_set(key, good, ttl=600)
    return good


def get_crypto_chain(currency, expiry_label, limit=30):
    key = f"chain:{currency}:{expiry_label}:{limit}"
    cached = cache_get(key)
    if cached is not None:
        return cached

    url = f"{DERIBIT}/public/get_book_summary_by_currency"
    params = {"currency": currency, "kind": "option"}
    r = http_get(url, params=params, timeout=20)
    data = r.json().get("result", [])

    marker = f"-{expiry_label}-"
    matched = [item for item in data if marker in item.get("instrument_name", "")]

    def strike_of(item):
        try:
            return float(item["instrument_name"].split("-")[2])
        except (ValueError, IndexError):
            return 0

    matched.sort(key=strike_of)
    spot = get_crypto_spot(currency) or 1.0

    if spot:
        matched.sort(key=lambda i: abs(strike_of(i) - spot))
        matched = matched[:limit]
        matched.sort(key=strike_of)

    rows = []
    for item in matched:
        name = item["instrument_name"]
        parts = name.split("-")
        try:
            strike = float(parts[2])
            opt_type = "call" if parts[3] == "C" else "put"
        except (IndexError, ValueError):
            continue

        # Deribit gives prices in BTC. Convert to USD.
        bid_btc = item.get("bid_price")
        ask_btc = item.get("ask_price")

        bid_usd = None
        ask_usd = None
        if bid_btc is not None and spot:
            bid_usd = round(float(bid_btc) * spot, 2)
        if ask_btc is not None and spot:
            ask_usd = round(float(ask_btc) * spot, 2)

        rows.append({
            "instrument": name,
            "type": opt_type,
            "strike": strike,
            "bid": bid_usd,
            "ask": ask_usd,
            "iv": item.get("mark_iv"),
            "delta": None,
            "oi": item.get("open_interest"),
        })

    cache_set(key, rows, ttl=60)
    return rows


def get_crypto_spot(currency="BTC"):
    key = f"spot:{currency}"
    cached = cache_get(key)
    if cached is not None:
        return cached
    try:
        index_name = f"{currency.lower()}_usd"
        r = http_get(
            f"{DERIBIT}/public/get_index_price",
            params={"index_name": index_name},
            timeout=10,
        )
        price = float(r.json()["result"]["index_price"])
        cache_set(key, price, ttl=30)
        return price
    except Exception:
        return None


# ---------- Stocks ----------
def _get_stock_ticker(symbol):
    return yf.Ticker(symbol, session=_stock_session)


def get_stock_expiries(symbol):
    key = f"stk_exp:{symbol}"
    cached = cache_get(key)
    if cached is not None:
        return cached
    try:
        t = _get_stock_ticker(symbol)
        expiries = list(t.options)
        result = [(e, e) for e in expiries[:8]]
        cache_set(key, result, ttl=3600)
        return result
    except Exception as e:
        print(f"[stocks] expiries error {symbol}: {e}")
        return []


def get_stock_spot(symbol):
    key = f"stk_spot:{symbol}"
    cached = cache_get(key)
    if cached is not None:
        return cached
    try:
        t = _get_stock_ticker(symbol)
        price = float(t.fast_info["last_price"])
        cache_set(key, price, ttl=60)
        return price
    except Exception as e:
        print(f"[stocks] spot error {symbol}: {e}")
        return None


def _clean(value):
    try:
        if value is None:
            return 0.0
        f = float(value)
        if f != f:
            return 0.0
        return f
    except Exception:
        return 0.0


def get_stock_chain(symbol, expiry, max_strikes=30):
    key = f"stk_chain:{symbol}:{expiry}:{max_strikes}"
    cached = cache_get(key)
    if cached is not None:
        return cached
    try:
        t = _get_stock_ticker(symbol)
        chain = t.option_chain(expiry)
    except Exception as e:
        print(f"[stocks] chain error {symbol} {expiry}: {e}")
        return []

    spot = get_stock_spot(symbol) or 0
    rows = []
    for _, r in chain.calls.iterrows():
        rows.append(_stock_row(r, symbol, expiry, "call"))
    for _, r in chain.puts.iterrows():
        rows.append(_stock_row(r, symbol, expiry, "put"))

    rows.sort(key=lambda x: abs(x["strike"] - spot))
    rows = rows[:max_strikes]
    rows.sort(key=lambda x: (x["strike"], 0 if x["type"] == "call" else 1))
    cache_set(key, rows, ttl=120)
    return rows


def _stock_row(r, symbol, expiry, opt_type):
    strike = _clean(r.get("strike"))
    bid = _clean(r.get("bid"))
    ask = _clean(r.get("ask"))
    last = _clean(r.get("lastPrice"))
    iv = _clean(r.get("impliedVolatility"))

    if bid == 0 and ask == 0 and last > 0:
        bid = round(last * 0.98, 2)
        ask = round(last * 1.02, 2)

    if iv < 0.001:
        iv = 0
    else:
        iv = iv * 100

    suffix = "C" if opt_type == "call" else "P"
    return {
        "instrument": f"{symbol}-{expiry}-{strike}-{suffix}",
        "type": opt_type,
        "strike": strike,
        "bid": bid,
        "ask": ask,
        "iv": iv,
        "delta": None,
        "oi": int(_clean(r.get("openInterest"))),
    }


# ---------- Charts ----------
def make_multi_leg_chart(spot, legs, symbol):
    if not legs:
        fig = go.Figure()
        fig.update_layout(
            paper_bgcolor=PANEL, plot_bgcolor=PANEL, font=dict(color=TEXT),
            annotations=[dict(text="Add legs or pick a preset",
                              x=0.5, y=0.5, xref="paper", yref="paper",
                              showarrow=False, font=dict(color=MUTED, size=14))],
        )
        return fig

    strikes = [l["strike"] for l in legs if l["type"] != "underlying"]
    all_levels = strikes + [spot] if strikes else [spot]
    low = min(all_levels) * 0.85
    high = max(all_levels) * 1.15
    step = (high - low) / 60
    prices = [low + i * step for i in range(61)]

    # For crypto, premium is in USD (already converted), spot is in USD.
    # For stocks, same. Good.
    total = []
    for p in prices:
        pnl = 0.0
        for leg in legs:
            side = leg["side"]
            prem = leg["premium"]
            if leg["type"] == "underlying":
                pnl += side * (p - spot)
            elif leg["type"] == "call":
                intrinsic = max(p - leg["strike"], 0)
                pnl += side * (intrinsic - prem)
            elif leg["type"] == "put":
                intrinsic = max(leg["strike"] - p, 0)
                pnl += side * (intrinsic - prem)
        total.append(pnl)

    fig = go.Figure()
    profit_x, profit_y = [], []
    loss_x, loss_y = [], []
    for x, y in zip(prices, total):
        if y >= 0:
            profit_x.append(x); profit_y.append(y)
        else:
            loss_x.append(x); loss_y.append(y)

    fig.add_trace(go.Scatter(
        x=profit_x, y=profit_y, mode="lines",
        line=dict(color=PROFIT, width=3),
        fill="tozeroy", fillcolor="rgba(46, 204, 113, 0.20)",
    ))
    fig.add_trace(go.Scatter(
        x=loss_x, y=loss_y, mode="lines",
        line=dict(color=LOSS, width=3),
        fill="tozeroy", fillcolor="rgba(231, 76, 60, 0.20)",
    ))

    fig.add_hline(y=0, line_dash="dash", line_color=MUTED)
    for s in sorted(set(strikes)):
        fig.add_vline(x=s, line_dash="dot", line_color=STRIKE, line_width=1,
                      annotation_text=f"{s}", annotation_position="top",
                      annotation_font=dict(color=STRIKE, size=10))
    fig.add_vline(x=spot, line_dash="dot", line_color=SPOT, line_width=2,
                  annotation_text=f"Spot {round(spot, 2)}",
                  annotation_position="bottom left",
                  annotation_font=dict(color=SPOT, size=11))

    fig.update_layout(
        title=dict(text=f"<b>Strategy — {symbol}</b> ({len(legs)} legs)",
                   font=dict(color=TEXT, size=16), x=0.02),
        xaxis=dict(title=dict(text=f"{symbol} Price at Expiry", font=dict(color=TEXT)),
                   tickfont=dict(color=MUTED), gridcolor=BORDER, zerolinecolor=BORDER),
        yaxis=dict(title=dict(text="Profit / Loss ($)", font=dict(color=TEXT)),
                   tickfont=dict(color=MUTED), gridcolor=BORDER, zerolinecolor=BORDER),
        paper_bgcolor=PANEL, plot_bgcolor=PANEL,
        font=dict(color=TEXT),
        hovermode="x unified",
        margin=dict(l=60, r=30, t=80, b=50),
        showlegend=False,
    )
    return fig


def make_preview_chart(spot, strike, premium, symbol):
    low = min(spot, strike) * 0.85
    high = max(spot, strike) * 1.15
    step = (high - low) / 60
    prices = [low + i * step for i in range(61)]

    payoffs = []
    for p in prices:
        if p <= strike:
            payoff = (p - spot) + premium
        else:
            payoff = (strike - spot) + premium
        payoffs.append(payoff)

    fig = go.Figure()
    profit_x, profit_y = [], []
    loss_x, loss_y = [], []
    for x, y in zip(prices, payoffs):
        if y >= 0:
            profit_x.append(x); profit_y.append(y)
        else:
            loss_x.append(x); loss_y.append(y)

    fig.add_trace(go.Scatter(
        x=profit_x, y=profit_y, mode="lines",
        line=dict(color=PROFIT, width=3),
        fill="tozeroy", fillcolor="rgba(46, 204, 113, 0.20)",
    ))
    fig.add_trace(go.Scatter(
        x=loss_x, y=loss_y, mode="lines",
        line=dict(color=LOSS, width=3),
        fill="tozeroy", fillcolor="rgba(231, 76, 60, 0.20)",
    ))

    fig.add_hline(y=0, line_dash="dash", line_color=MUTED)
    fig.add_vline(x=strike, line_dash="dot", line_color=STRIKE,
                  annotation_text=f"Strike {strike}", annotation_position="top right",
                  annotation_font=dict(color=STRIKE, size=12))
    fig.add_vline(x=spot, line_dash="dot", line_color=SPOT,
                  annotation_text=f"Spot {round(spot, 2)}", annotation_position="bottom left",
                  annotation_font=dict(color=SPOT, size=11))

    fig.update_layout(
        title=dict(text=f"<b>Covered Call Preview — {symbol}</b><br>"
                        f"<span style='font-size:12px;color:{MUTED}'>"
                        f"Buy at {round(spot, 2)} | Sell {strike} Call for {round(premium, 2)}</span>",
                   font=dict(color=TEXT, size=16), x=0.02),
        xaxis=dict(title=dict(text=f"{symbol} Price at Expiry", font=dict(color=TEXT)),
                   tickfont=dict(color=MUTED), gridcolor=BORDER, zerolinecolor=BORDER),
        yaxis=dict(title=dict(text="Profit / Loss ($)", font=dict(color=TEXT)),
                   tickfont=dict(color=MUTED), gridcolor=BORDER, zerolinecolor=BORDER),
        paper_bgcolor=PANEL, plot_bgcolor=PANEL,
        font=dict(color=TEXT),
        hovermode="x unified",
        margin=dict(l=60, r=30, t=80, b=50),
        showlegend=False,
    )
    return fig


app = Dash(__name__)
server = app.server


app.layout = html.Div([
    html.Div([
        html.H1("Options Dashboard v2",
                style={"margin": "0", "fontSize": "22px", "fontWeight": "600"}),
        html.P("Multi-leg strategy builder — prices in USD",
               style={"margin": "4px 0 0 0", "fontSize": "12px", "color": MUTED}),
    ], style={"padding": "16px 24px", "borderBottom": f"1px solid {BORDER}"}),

    html.Div([
        html.Span("Symbol:",
                  style={"marginRight": "12px", "fontSize": "13px", "fontWeight": "600"}),
        html.Div(id="symbol-buttons", style={"display": "inline-block"}),
    ], style={"display": "flex", "alignItems": "center", "padding": "12px 24px 0 24px"}),

    html.Div([
        html.Span("Expiry:",
                  style={"marginRight": "12px", "fontSize": "13px", "fontWeight": "600"}),
        html.Div(id="expiry-buttons", style={"display": "inline-block"}),
    ], style={"display": "flex", "alignItems": "center", "padding": "12px 24px"}),

    html.Div([
        html.Span("Presets:",
                  style={"marginRight": "12px", "fontSize": "13px", "fontWeight": "600"}),
        html.Button("Covered Call", id="preset-cc", n_clicks=0,
                    style={"padding": "6px 12px", "marginRight": "6px",
                           "borderRadius": "5px", "border": f"1px solid {BORDER}",
                           "background": "#21262d", "color": TEXT,
                           "fontSize": "12px", "cursor": "pointer"}),
        html.Button("Call Spread", id="preset-cs", n_clicks=0,
                    style={"padding": "6px 12px", "marginRight": "6px",
                           "borderRadius": "5px", "border": f"1px solid {BORDER}",
                           "background": "#21262d", "color": TEXT,
                           "fontSize": "12px", "cursor": "pointer"}),
        html.Button("Iron Condor", id="preset-ic", n_clicks=0,
                    style={"padding": "6px 12px", "marginRight": "6px",
                           "borderRadius": "5px", "border": f"1px solid {BORDER}",
                           "background": "#21262d", "color": TEXT,
                           "fontSize": "12px", "cursor": "pointer"}),
        html.Button("Straddle", id="preset-st", n_clicks=0,
                    style={"padding": "6px 12px",
                           "borderRadius": "5px", "border": f"1px solid {BORDER}",
                           "background": "#21262d", "color": TEXT,
                           "fontSize": "12px", "cursor": "pointer"}),
    ], style={"display": "flex", "alignItems": "center",
              "padding": "0 24px 12px 24px"}),

    html.Div([
        html.Div([
            html.Div([
                html.Span("Options Chain",
                          style={"fontWeight": "600", "fontSize": "14px"}),
                html.Span(id="row-count",
                          style={"fontSize": "12px", "marginLeft": "8px", "color": MUTED}),

                html.Div([
                    html.Button("All", id={"type": "filter-btn", "value": "all"}, n_clicks=0,
                                style={"padding": "5px 12px", "marginLeft": "16px",
                                       "borderRadius": "5px",
                                       "border": f"1px solid {BORDER}",
                                       "background": ACCENT, "color": "#ffffff",
                                       "fontSize": "11px", "cursor": "pointer",
                                       "fontWeight": "600"}),
                    html.Button("Calls", id={"type": "filter-btn", "value": "call"}, n_clicks=0,
                                style={"padding": "5px 12px", "marginLeft": "4px",
                                       "borderRadius": "5px",
                                       "border": f"1px solid {BORDER}",
                                       "background": "#21262d", "color": CALL_COLOR,
                                       "fontSize": "11px", "cursor": "pointer",
                                       "fontWeight": "600"}),
                    html.Button("Puts", id={"type": "filter-btn", "value": "put"}, n_clicks=0,
                                style={"padding": "5px 12px", "marginLeft": "4px",
                                       "borderRadius": "5px",
                                       "border": f"1px solid {BORDER}",
                                       "background": "#21262d", "color": PUT_COLOR,
                                       "fontSize": "11px", "cursor": "pointer",
                                       "fontWeight": "600"}),
                ], style={"display": "inline-block"}),

                html.Div([
                    html.Button("+ LONG", id="add-long-btn", n_clicks=0,
                                style={"padding": "5px 10px", "marginLeft": "12px",
                                       "borderRadius": "5px",
                                       "border": f"1px solid {PROFIT}",
                                       "background": "transparent",
                                       "color": PROFIT, "fontSize": "11px",
                                       "cursor": "pointer", "fontWeight": "600"}),
                    html.Button("+ SHORT", id="add-short-btn", n_clicks=0,
                                style={"padding": "5px 10px", "marginLeft": "6px",
                                       "borderRadius": "5px",
                                       "border": f"1px solid {RED}",
                                       "background": "transparent",
                                       "color": RED, "fontSize": "11px",
                                       "cursor": "pointer", "fontWeight": "600"}),
                ], style={"display": "inline-block"}),
            ], style={"padding": "12px 16px", "borderBottom": f"1px solid {BORDER}"}),

            dag.AgGrid(
                id="chain-grid",
                columnDefs=[
                    {"field": "instrument", "headerName": "Instrument", "flex": 2},
                    {"field": "type", "headerName": "Type", "flex": 1,
                     "cellStyle": {"function": "params.value === 'call' ? {color: '#2ecc71', fontWeight: 600} : {color: '#e74c3c', fontWeight: 600}"}},
                    {"field": "strike", "headerName": "Strike", "flex": 1,
                     "valueFormatter": {"function": "params.value ? '$' + params.value.toLocaleString() : ''"}},
                    {"field": "bid", "headerName": "Bid", "flex": 1,
                     "valueFormatter": {"function": "params.value != null ? '$' + Number(params.value).toFixed(2) : ''"}},
                    {"field": "ask", "headerName": "Ask", "flex": 1,
                     "valueFormatter": {"function": "params.value != null ? '$' + Number(params.value).toFixed(2) : ''"}},
                    {"field": "iv", "headerName": "IV", "flex": 1,
                     "valueFormatter": {"function": "params.value ? Number(params.value).toFixed(1) + '%' : ''"}},
                    {"field": "oi", "headerName": "OI", "flex": 1},
                ],
                rowData=[],
                style={"height": "calc(100vh - 400px)"},
                className="ag-theme-alpine-dark",
                dashGridOptions={
                    "rowSelection": "single",
                    "animateRows": False,
                    "suppressCellFocus": True,
                    "getRowStyle": {"function": "params.data && params.data.type === 'call' ? {background: 'rgba(46, 204, 113, 0.06)'} : (params.data && params.data.type === 'put' ? {background: 'rgba(231, 76, 60, 0.06)'} : null)"},
                },
            ),

            html.Div([
                html.Div([
                    html.Span("Strategy Legs",
                              style={"fontWeight": "600", "fontSize": "13px"}),
                    html.Button("+ Underlying", id="add-underlying-btn", n_clicks=0,
                                style={"padding": "4px 10px", "marginLeft": "12px",
                                       "borderRadius": "4px",
                                       "border": f"1px solid {ACCENT}",
                                       "background": "transparent",
                                       "color": ACCENT, "fontSize": "11px",
                                       "cursor": "pointer"}),
                    html.Button("Clear All", id="clear-legs-btn", n_clicks=0,
                                style={"padding": "4px 10px", "marginLeft": "6px",
                                       "borderRadius": "4px",
                                       "border": f"1px solid {BORDER}",
                                       "background": "transparent",
                                       "color": TEXT, "fontSize": "11px",
                                       "cursor": "pointer"}),
                ], style={"marginBottom": "8px"}),
                html.Div(id="legs-list",
                         children=html.Span("No legs yet — click a row for preview",
                                            style={"fontSize": "12px", "color": MUTED})),
            ], style={
                "padding": "12px 16px",
                "borderTop": f"1px solid {BORDER}",
                "minHeight": "100px",
                "maxHeight": "180px",
                "overflowY": "auto",
            }),
        ], style={
            "background": PANEL,
            "borderRadius": "8px",
            "border": f"1px solid {BORDER}",
            "overflow": "hidden",
        }),

        html.Div([
            dcc.Graph(id="chart", style={"height": "calc(100vh - 240px)"},
                      config={"displayModeBar": False}),
        ], style={
            "background": PANEL,
            "borderRadius": "8px",
            "border": f"1px solid {BORDER}",
            "overflow": "hidden",
        }),
    ], style={
        "display": "grid",
        "gridTemplateColumns": "1fr 1fr",
        "gap": "16px",
        "padding": "16px 24px",
    }),

    dcc.Interval(id="tick", interval=30000, n_intervals=0),
    dcc.Store(id="symbol-store", data="BTC"),
    dcc.Store(id="expiry-store", data=None),
    dcc.Store(id="expiry-list", data=[]),
    dcc.Store(id="legs-store", data=[]),
    dcc.Store(id="filter-store", data="all"),
    dcc.Store(id="rows-store", data=[]),
], style={
    "minHeight": "100vh",
    "fontFamily": "Inter, -apple-system, Segoe UI, sans-serif",
    "background": BG,
    "color": TEXT,
})


@callback(
    Output("symbol-buttons", "children"),
    Input("symbol-store", "data"),
)
def render_symbol_buttons(active):
    buttons = []
    for sym in ["BTC", "ETH", "AAPL", "SPY", "TSLA"]:
        is_active = (sym == active)
        buttons.append(html.Button(
            sym,
            id={"type": "symbol-btn", "value": sym},
            n_clicks=0,
            style={
                "padding": "8px 16px", "marginRight": "6px",
                "borderRadius": "6px", "border": f"1px solid {BORDER}",
                "background": ACCENT if is_active else "#21262d",
                "color": "#ffffff", "fontSize": "13px",
                "fontWeight": "600" if is_active else "400",
                "cursor": "pointer",
            },
        ))
    return buttons


@callback(
    Output("symbol-store", "data", allow_duplicate=True),
    Input({"type": "symbol-btn", "value": dash_all}, "n_clicks"),
    prevent_initial_call=True,
)
def on_symbol_click(_):
    if not ctx.triggered_id:
        return no_update
    return ctx.triggered_id["value"]


@callback(
    Output("filter-store", "data"),
    Input({"type": "filter-btn", "value": dash_all}, "n_clicks"),
    prevent_initial_call=True,
)
def on_filter_click(_):
    if not ctx.triggered_id:
        return no_update
    return ctx.triggered_id["value"]


@callback(
    Output("expiry-list", "data"),
    Output("expiry-store", "data", allow_duplicate=True),
    Input("symbol-store", "data"),
    prevent_initial_call="initial_duplicate",
)
def load_expiries_for_symbol(symbol):
    if not symbol:
        return [], None
    try:
        if symbol in CRYPTO_SYMBOLS:
            expiries = get_crypto_expiries(currency=symbol)
            data = [[ts, label] for ts, label in expiries[:6]]
            default = expiries[0][1] if expiries else None
        else:
            expiries = get_stock_expiries(symbol)
            data = [[label, label] for ts, label in expiries[:6]]
            default = expiries[0][1] if expiries else None
    except Exception as e:
        print(f"[expiries] Failed: {e}")
        return [], None
    return data, default


@callback(
    Output("expiry-buttons", "children"),
    Input("expiry-list", "data"),
    Input("expiry-store", "data"),
)
def render_expiry_buttons(expiry_list, active):
    if not expiry_list:
        return html.Span("Loading expiries…",
                         style={"fontSize": "12px", "color": MUTED})
    buttons = []
    for ts, label in expiry_list:
        is_active = (str(label) == str(active))
        buttons.append(html.Button(
            label,
            id={"type": "expiry-btn", "value": str(label)},
            n_clicks=0,
            style={
                "padding": "6px 10px", "marginRight": "6px",
                "borderRadius": "5px", "border": f"1px solid {BORDER}",
                "background": ACCENT if is_active else "#21262d",
                "color": "#ffffff", "fontSize": "11px",
                "cursor": "pointer",
            },
        ))
    return buttons


@callback(
    Output("expiry-store", "data", allow_duplicate=True),
    Input({"type": "expiry-btn", "value": dash_all}, "n_clicks"),
    prevent_initial_call=True,
)
def on_expiry_click(_):
    if not ctx.triggered_id:
        return no_update
    return ctx.triggered_id["value"]


@callback(
    Output({"type": "filter-btn", "value": dash_all}, "style"),
    Input("filter-store", "data"),
    State({"type": "filter-btn", "value": dash_all}, "value"),
    prevent_initial_call=True,
)
def style_filter_buttons(active, _):
    styles = []
    for value in ["all", "call", "put"]:
        is_active = (value == active)
        if value == "all":
            color = "#ffffff"
        elif value == "call":
            color = CALL_COLOR
        else:
            color = PUT_COLOR
        styles.append({
            "padding": "5px 12px",
            "marginLeft": "16px" if value == "all" else "4px",
            "borderRadius": "5px",
            "border": f"1px solid {BORDER}",
            "background": ACCENT if is_active else "#21262d",
            "color": "#ffffff" if is_active else color,
            "fontSize": "11px",
            "cursor": "pointer",
            "fontWeight": "600",
        })
    return styles


@callback(
    Output("rows-store", "data"),
    Input("tick", "n_intervals"),
    Input("symbol-store", "data"),
    Input("expiry-store", "data"),
    State("expiry-list", "data"),
    prevent_initial_call=True,
)
def fetch_rows(_, symbol, expiry, expiry_list):
    if not symbol or not expiry or not expiry_list:
        return []
    valid_labels = {str(label) for _, label in expiry_list}
    if str(expiry) not in valid_labels:
        return []
    try:
        if symbol in CRYPTO_SYMBOLS:
            return get_crypto_chain(symbol, expiry, 30)
        else:
            return get_stock_chain(symbol, expiry, 30)
    except Exception as e:
        print(f"[fetch] error: {e}")
        return []


@callback(
    Output("chain-grid", "rowData"),
    Output("row-count", "children"),
    Output("chain-grid", "selectedRows", allow_duplicate=True),
    Input("rows-store", "data"),
    Input("filter-store", "data"),
    State("chain-grid", "selectedRows"),
    prevent_initial_call=True,
)
def apply_filter(rows, filter_value, current_selected):
    if not rows:
        return [], "0 contracts", no_update

    if filter_value == "call":
        filtered = [r for r in rows if r["type"] == "call"]
    elif filter_value == "put":
        filtered = [r for r in rows if r["type"] == "put"]
    else:
        filtered = rows

    selected = current_selected
    if not selected and filtered:
        selected = [filtered[0]]

    return filtered, f"{len(filtered)} contracts", selected


@callback(
    Output("legs-store", "data", allow_duplicate=True),
    Input("add-long-btn", "n_clicks"),
    State("chain-grid", "selectedRows"),
    State("legs-store", "data"),
    prevent_initial_call=True,
)
def add_long(n, selected, legs):
    if not selected or n == 0:
        return legs
    row = selected[0]
    leg = {"side": 1, "type": row["type"], "strike": row["strike"],
           "premium": row.get("bid") or 0, "instrument": row["instrument"]}
    return (legs or []) + [leg]


@callback(
    Output("legs-store", "data", allow_duplicate=True),
    Input("add-short-btn", "n_clicks"),
    State("chain-grid", "selectedRows"),
    State("legs-store", "data"),
    prevent_initial_call=True,
)
def add_short(n, selected, legs):
    if not selected or n == 0:
        return legs
    row = selected[0]
    leg = {"side": -1, "type": row["type"], "strike": row["strike"],
           "premium": row.get("bid") or 0, "instrument": row["instrument"]}
    return (legs or []) + [leg]


@callback(
    Output("legs-store", "data", allow_duplicate=True),
    Input("add-underlying-btn", "n_clicks"),
    State("symbol-store", "data"),
    State("legs-store", "data"),
    prevent_initial_call=True,
)
def add_underlying(n, symbol, legs):
    if n == 0:
        return legs
    leg = {"side": 1, "type": "underlying", "strike": 0, "premium": 0,
           "instrument": symbol}
    return (legs or []) + [leg]


@callback(
    Output("legs-store", "data", allow_duplicate=True),
    Input("clear-legs-btn", "n_clicks"),
    prevent_initial_call=True,
)
def clear_legs(n):
    if n:
        return []
    return no_update


@callback(
    Output("legs-store", "data", allow_duplicate=True),
    Input("preset-cc", "n_clicks"),
    State("symbol-store", "data"),
    State("rows-store", "data"),
    prevent_initial_call=True,
)
def preset_covered_call(n, symbol, rows):
    if not n or not rows:
        return no_update
    spot = get_crypto_spot(symbol) if symbol in CRYPTO_SYMBOLS else get_stock_spot(symbol)
    if spot is None:
        return no_update
    calls = [r for r in rows if r["type"] == "call" and r["strike"] > spot]
    calls.sort(key=lambda r: r["strike"])
    if not calls:
        return no_update
    call = calls[0]
    return [
        {"side": 1, "type": "underlying", "strike": 0, "premium": 0, "instrument": symbol},
        {"side": -1, "type": "call", "strike": call["strike"],
         "premium": call.get("bid") or 0, "instrument": call["instrument"]},
    ]


@callback(
    Output("legs-store", "data", allow_duplicate=True),
    Input("preset-cs", "n_clicks"),
    State("symbol-store", "data"),
    State("rows-store", "data"),
    prevent_initial_call=True,
)
def preset_call_spread(n, symbol, rows):
    if not n or not rows:
        return no_update
    spot = get_crypto_spot(symbol) if symbol in CRYPTO_SYMBOLS else get_stock_spot(symbol)
    if spot is None:
        return no_update
    calls = sorted([r for r in rows if r["type"] == "call"], key=lambda r: r["strike"])
    otm = [c for c in calls if c["strike"] > spot]
    if len(otm) < 2:
        return no_update
    l, s = otm[0], otm[1]
    return [
        {"side": 1, "type": "call", "strike": l["strike"],
         "premium": l.get("ask") or l.get("bid") or 0, "instrument": l["instrument"]},
        {"side": -1, "type": "call", "strike": s["strike"],
         "premium": s.get("bid") or 0, "instrument": s["instrument"]},
    ]


@callback(
    Output("legs-store", "data", allow_duplicate=True),
    Input("preset-ic", "n_clicks"),
    State("symbol-store", "data"),
    State("rows-store", "data"),
    prevent_initial_call=True,
)
def preset_iron_condor(n, symbol, rows):
    if not n or not rows:
        return no_update
    spot = get_crypto_spot(symbol) if symbol in CRYPTO_SYMBOLS else get_stock_spot(symbol)
    if spot is None:
        return no_update
    calls = sorted([r for r in rows if r["type"] == "call"], key=lambda r: r["strike"])
    puts = sorted([r for r in rows if r["type"] == "put"], key=lambda r: r["strike"])
    oc = [c for c in calls if c["strike"] > spot]
    op = [p for p in puts if p["strike"] < spot]
    if len(oc) < 2 or len(op) < 2:
        return no_update
    return [
        {"side": 1, "type": "put", "strike": op[0]["strike"],
         "premium": op[0].get("ask") or 0, "instrument": op[0]["instrument"]},
        {"side": -1, "type": "put", "strike": op[1]["strike"],
         "premium": op[1].get("bid") or 0, "instrument": op[1]["instrument"]},
        {"side": -1, "type": "call", "strike": oc[0]["strike"],
         "premium": oc[0].get("bid") or 0, "instrument": oc[0]["instrument"]},
        {"side": 1, "type": "call", "strike": oc[1]["strike"],
         "premium": oc[1].get("ask") or 0, "instrument": oc[1]["instrument"]},
    ]


@callback(
    Output("legs-store", "data", allow_duplicate=True),
    Input("preset-st", "n_clicks"),
    State("symbol-store", "data"),
    State("rows-store", "data"),
    prevent_initial_call=True,
)
def preset_straddle(n, symbol, rows):
    if not n or not rows:
        return no_update
    spot = get_crypto_spot(symbol) if symbol in CRYPTO_SYMBOLS else get_stock_spot(symbol)
    if spot is None:
        return no_update
    calls = sorted([r for r in rows if r["type"] == "call"], key=lambda r: abs(r["strike"] - spot))
    puts = sorted([r for r in rows if r["type"] == "put"], key=lambda r: abs(r["strike"] - spot))
    if not calls or not puts:
        return no_update
    c, p = calls[0], puts[0]
    return [
        {"side": 1, "type": "call", "strike": c["strike"],
         "premium": c.get("ask") or 0, "instrument": c["instrument"]},
        {"side": 1, "type": "put", "strike": p["strike"],
         "premium": p.get("ask") or 0, "instrument": p["instrument"]},
    ]


@callback(
    Output("legs-list", "children"),
    Input("legs-store", "data"),
)
def render_legs(legs):
    if not legs:
        return html.Span("No legs yet — click a row for preview",
                         style={"fontSize": "12px", "color": MUTED})

    items = []
    for i, leg in enumerate(legs):
        color = PROFIT if leg["side"] > 0 else RED
        side_text = "LONG" if leg["side"] > 0 else "SHORT"
        if leg["type"] == "underlying":
            detail = f"{leg['instrument']} (spot)"
        else:
            detail = f"{leg['type'].upper()} K={leg['strike']} @ ${round(leg['premium'], 2)}"
        items.append(html.Div([
            html.Span(f"#{i+1} ", style={"color": MUTED, "fontSize": "11px"}),
            html.Span(f"{side_text} ", style={"color": color, "fontWeight": "600", "fontSize": "12px"}),
            html.Span(detail, style={"color": TEXT, "fontSize": "12px"}),
        ], style={"padding": "3px 0", "borderBottom": f"1px solid {BORDER}"}))
    return items


@callback(
    Output("chart", "figure"),
    Input("legs-store", "data"),
    Input("chain-grid", "selectedRows"),
    State("symbol-store", "data"),
    prevent_initial_call=False,
)
def update_chart(legs, selected, symbol):
    symbol = symbol or "BTC"
    if symbol in CRYPTO_SYMBOLS:
        spot = get_crypto_spot(symbol)
    else:
        spot = get_stock_spot(symbol)
    if spot is None:
        spot = 100

    if legs:
        return make_multi_leg_chart(spot, legs, symbol)

    if selected:
        row = selected[0]
        strike = row.get("strike", 0)
        premium = row.get("bid") or 0
        if strike:
            return make_preview_chart(spot, strike, premium, symbol)

    fig = go.Figure()
    fig.update_layout(
        paper_bgcolor=PANEL, plot_bgcolor=PANEL, font=dict(color=TEXT),
        annotations=[dict(text="Loading…",
                          x=0.5, y=0.5, xref="paper", yref="paper",
                          showarrow=False, font=dict(color=MUTED, size=14))],
    )
    return fig


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8051))
    app.run(debug=False, host="0.0.0.0", port=port)