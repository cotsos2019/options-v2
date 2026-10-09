"""
Options Dashboard v2 — Stage 6
Multi-leg + underlying + presets.
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

CRYPTO_SYMBOLS = {"BTC", "ETH"}

_stock_session = curl_requests.Session(impersonate="chrome")
_stock_session.verify = False


def http_get(url, params=None, timeout=15):
    try:
        return requests.get(url, params=params, timeout=timeout)
    except requests.exceptions.SSLError:
        return requests.get(url, params=params, timeout=timeout, verify=False)


# ---------- Crypto: Deribit ----------
def get_crypto_expiries(currency="BTC"):
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
    return good


def get_crypto_chain(currency, expiry_label, limit=30):
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
    spot = get_crypto_spot(currency)
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

        rows.append({
            "instrument": name,
            "type": opt_type,
            "strike": strike,
            "bid": item.get("bid_price"),
            "ask": item.get("ask_price"),
            "iv": item.get("mark_iv"),
            "delta": None,
            "oi": item.get("open_interest"),
        })

    print(f"[crypto] {currency} {expiry_label}: {len(rows)} rows")
    return rows


def get_crypto_spot(currency="BTC"):
    try:
        index_name = f"{currency.lower()}_usd"
        r = http_get(
            f"{DERIBIT}/public/get_index_price",
            params={"index_name": index_name},
            timeout=10,
        )
        return float(r.json()["result"]["index_price"])
    except Exception:
        return None


# ---------- Stocks: yfinance ----------
def _get_stock_ticker(symbol):
    return yf.Ticker(symbol, session=_stock_session)


def get_stock_expiries(symbol):
    try:
        t = _get_stock_ticker(symbol)
        expiries = list(t.options)
        print(f"[stocks] {symbol} expiries: {len(expiries)}")
        return [(e, e) for e in expiries[:8]]
    except Exception as e:
        print(f"[stocks] expiries error {symbol}: {e}")
        return []


def get_stock_spot(symbol):
    try:
        t = _get_stock_ticker(symbol)
        return float(t.fast_info["last_price"])
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
    try:
        t = _get_stock_ticker(symbol)
        chain = t.option_chain(expiry)
        print(f"[stocks] {symbol} {expiry}: calls={len(chain.calls)} puts={len(chain.puts)}")
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


# ---------- Multi-leg chart ----------
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
            profit_x.append(x)
            profit_y.append(y)
        else:
            loss_x.append(x)
            loss_y.append(y)

    fig.add_trace(go.Scatter(
        x=profit_x, y=profit_y, mode="lines",
        line=dict(color=PROFIT, width=3),
        fill="tozeroy", fillcolor="rgba(46, 204, 113, 0.20)",
        name="Profit",
    ))
    fig.add_trace(go.Scatter(
        x=loss_x, y=loss_y, mode="lines",
        line=dict(color=LOSS, width=3),
        fill="tozeroy", fillcolor="rgba(231, 76, 60, 0.20)",
        name="Loss",
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

    title = f"<b>Strategy — {symbol}</b> ({len(legs)} legs)"

    fig.update_layout(
        title=dict(text=title, font=dict(color=TEXT, size=16), x=0.02),
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
        html.P("Multi-leg strategy builder with presets",
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

    # Preset row
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
        # LEFT
        html.Div([
            html.Div([
                html.Span("Options Chain",
                          style={"fontWeight": "600", "fontSize": "14px"}),
                html.Span(id="row-count",
                          style={"fontSize": "12px", "marginLeft": "8px", "color": MUTED}),
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
                    {"field": "type", "headerName": "Type", "flex": 1},
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
                         children=html.Span("No legs yet",
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

        # RIGHT
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

    dcc.Interval(id="tick", interval=15000, n_intervals=0),
    dcc.Store(id="symbol-store", data="BTC"),
    dcc.Store(id="expiry-store", data=None),
    dcc.Store(id="expiry-list", data=[]),
    dcc.Store(id="legs-store", data=[]),
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

    print(f"[expiries] {symbol}: default={default}")
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
    Output("chain-grid", "rowData", allow_duplicate=True),
    Output("row-count", "children", allow_duplicate=True),
    Input("tick", "n_intervals"),
    Input("symbol-store", "data"),
    Input("expiry-store", "data"),
    State("expiry-list", "data"),
    prevent_initial_call=True,
)
def refresh(_, symbol, expiry, expiry_list):
    if not symbol or not expiry or not expiry_list:
        return [], "Loading…"

    valid_labels = {str(label) for _, label in expiry_list}
    if str(expiry) not in valid_labels:
        return [], "Loading…"

    try:
        if symbol in CRYPTO_SYMBOLS:
            rows = get_crypto_chain(symbol, expiry, 30)
        else:
            rows = get_stock_chain(symbol, expiry, 30)
    except Exception as e:
        print(f"[refresh] error: {e}")
        return [], "error"

    return rows, f"{len(rows)} contracts"


# ---------- Add leg (long) ----------
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
    leg = {
        "side": 1,
        "type": row["type"],
        "strike": row["strike"],
        "premium": row.get("bid") or 0,
        "instrument": row["instrument"],
    }
    legs = legs or []
    return legs + [leg]


# ---------- Add leg (short) ----------
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
    leg = {
        "side": -1,
        "type": row["type"],
        "strike": row["strike"],
        "premium": row.get("bid") or 0,
        "instrument": row["instrument"],
    }
    legs = legs or []
    return legs + [leg]


# ---------- Add underlying ----------
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
    leg = {
        "side": 1,
        "type": "underlying",
        "strike": 0,
        "premium": 0,
        "instrument": symbol,
    }
    legs = legs or []
    return legs + [leg]


# ---------- Clear legs ----------
@callback(
    Output("legs-store", "data", allow_duplicate=True),
    Input("clear-legs-btn", "n_clicks"),
    prevent_initial_call=True,
)
def clear_legs(n):
    if n:
        return []
    return no_update


# ---------- Presets ----------
@callback(
    Output("legs-store", "data", allow_duplicate=True),
    Input("preset-cc", "n_clicks"),
    State("symbol-store", "data"),
    State("chain-grid", "rowData"),
    prevent_initial_call=True,
)
def preset_covered_call(n, symbol, rows):
    if not n or not rows:
        return no_update

    spot = get_crypto_spot(symbol) if symbol in CRYPTO_SYMBOLS else get_stock_spot(symbol)
    if spot is None:
        return no_update

    # Pick nearest OTM call
    calls = [r for r in rows if r["type"] == "call" and r["strike"] > spot]
    calls.sort(key=lambda r: r["strike"])
    if not calls:
        return no_update

    call = calls[0]
    return [
        {"side": 1, "type": "underlying", "strike": 0, "premium": 0,
         "instrument": symbol},
        {"side": -1, "type": "call", "strike": call["strike"],
         "premium": call.get("bid") or 0, "instrument": call["instrument"]},
    ]


@callback(
    Output("legs-store", "data", allow_duplicate=True),
    Input("preset-cs", "n_clicks"),
    State("symbol-store", "data"),
    State("chain-grid", "rowData"),
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

    long_leg = otm[0]
    short_leg = otm[1]
    return [
        {"side": 1, "type": "call", "strike": long_leg["strike"],
         "premium": long_leg.get("ask") or long_leg.get("bid") or 0,
         "instrument": long_leg["instrument"]},
        {"side": -1, "type": "call", "strike": short_leg["strike"],
         "premium": short_leg.get("bid") or 0, "instrument": short_leg["instrument"]},
    ]


@callback(
    Output("legs-store", "data", allow_duplicate=True),
    Input("preset-ic", "n_clicks"),
    State("symbol-store", "data"),
    State("chain-grid", "rowData"),
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

    otm_calls = [c for c in calls if c["strike"] > spot]
    otm_puts = [p for p in puts if p["strike"] < spot]

    if len(otm_calls) < 2 or len(otm_puts) < 2:
        return no_update

    return [
        {"side": 1, "type": "put", "strike": otm_puts[0]["strike"],
         "premium": otm_puts[0].get("ask") or 0, "instrument": otm_puts[0]["instrument"]},
        {"side": -1, "type": "put", "strike": otm_puts[1]["strike"],
         "premium": otm_puts[1].get("bid") or 0, "instrument": otm_puts[1]["instrument"]},
        {"side": -1, "type": "call", "strike": otm_calls[0]["strike"],
         "premium": otm_calls[0].get("bid") or 0, "instrument": otm_calls[0]["instrument"]},
        {"side": 1, "type": "call", "strike": otm_calls[1]["strike"],
         "premium": otm_calls[1].get("ask") or 0, "instrument": otm_calls[1]["instrument"]},
    ]


@callback(
    Output("legs-store", "data", allow_duplicate=True),
    Input("preset-st", "n_clicks"),
    State("symbol-store", "data"),
    State("chain-grid", "rowData"),
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

    c = calls[0]
    p = puts[0]
    return [
        {"side": 1, "type": "call", "strike": c["strike"],
         "premium": c.get("ask") or 0, "instrument": c["instrument"]},
        {"side": 1, "type": "put", "strike": p["strike"],
         "premium": p.get("ask") or 0, "instrument": p["instrument"]},
    ]


# ---------- Render legs list ----------
@callback(
    Output("legs-list", "children"),
    Input("legs-store", "data"),
)
def render_legs(legs):
    if not legs:
        return html.Span("No legs yet",
                         style={"fontSize": "12px", "color": MUTED})

    items = []
    for i, leg in enumerate(legs):
        color = PROFIT if leg["side"] > 0 else RED
        side_text = "LONG" if leg["side"] > 0 else "SHORT"

        if leg["type"] == "underlying":
            detail = f"{leg['instrument']} (spot)"
        else:
            detail = f"{leg['type'].upper()} K={leg['strike']} @ {round(leg['premium'], 4)}"

        items.append(html.Div([
            html.Span(f"#{i+1} ", style={"color": MUTED, "fontSize": "11px"}),
            html.Span(f"{side_text} ", style={"color": color, "fontWeight": "600", "fontSize": "12px"}),
            html.Span(detail, style={"color": TEXT, "fontSize": "12px"}),
        ], style={"padding": "3px 0", "borderBottom": f"1px solid {BORDER}"}))
    return items


@callback(
    Output("chain-grid", "selectedRows", allow_duplicate=True),
    Input("chain-grid", "rowData"),
    State("chain-grid", "selectedRows"),
    prevent_initial_call=True,
)
def auto_select(row_data, current):
    if current:
        return current
    if not row_data:
        return []
    return [row_data[0]]


@callback(
    Output("chart", "figure"),
    Input("legs-store", "data"),
    State("symbol-store", "data"),
    prevent_initial_call=False,
)
def update_chart(legs, symbol):
    symbol = symbol or "BTC"

    if symbol in CRYPTO_SYMBOLS:
        spot = get_crypto_spot(symbol)
    else:
        spot = get_stock_spot(symbol)

    if spot is None:
        spot = 100

    return make_multi_leg_chart(spot, legs or [], symbol)


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8051))
    app.run(debug=False, host="0.0.0.0", port=port)