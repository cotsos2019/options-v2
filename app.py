"""
Options Dashboard v2 — Stage 15
+ Clear labels: presets are auto (from spot), LONG/SHORT are manual (from user selection).
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


STRINGS = {
    "el": {
        "title": "📊 Options Dashboard",
        "subtitle": "Crypto + Stocks options dashboard",
        "symbol": "💰 Σύμβολο:",
        "expiry": "📅 Λήξη:",
        "presets": "⚡ Στρατηγικές (auto από spot):",
        "presets_hint": "👉 Αυτόματες — επιλέγουν strikes με βάση το spot",
        "chain": "📋 Options Chain",
        "legs": "🎯 Στρατηγική (Legs)",
        "all": "ΟΛΑ", "calls": "CALLS", "puts": "PUTS",
        "long": "＋ LONG", "short": "－ SHORT",
        "manual_hint": "👉 Manual — βάζεις τα strikes που διάλεξες στο grid",
        "underlying": "＋ Υποκείμενο", "clear": "🗑️ Καθαρισμός",
        "no_legs": "Δεν υπάρχουν legs — κλίκαρε μια γραμμή για preview",
        "contracts": "συμβόλαια",
        "preset_cc": "🛡️ Covered Call",
        "preset_cs": "↗️ Call Spread",
        "preset_ic": "🦅 Iron Condor",
        "preset_st": "⚖️ Straddle",
        "about_btn": "❓ Τι είναι αυτό;",
        "analysis_btn": "📊 Ανάλυση Στρατηγικής",
        "guide_title": "📖 Οδηγός Στρατηγικών",
        "analysis_title": "📊 Ανάλυση της Στρατηγικής σου",
        "analysis_no_legs": "⚠️ Δεν έχεις προσθέσει legs ακόμα. Κλίκαρε μια γραμμή στο grid και πάτα **+ LONG** ή **+ SHORT**, ή διάλεξε ένα preset.",
        "analysis_your_legs": "🎯 Τα legs σου",
        "analysis_chart": "📈 Διάγραμμα Κέρδους / Ζημιάς",
        "analysis_scenarios": "🎲 Σενάρια — Πότε κερδίζεις και πότε χάνεις",
        "analysis_summary": "💰 Σύνοψη",
        "analysis_max_profit": "Μέγιστο κέρδος",
        "analysis_max_loss": "Μέγιστη ζημιά",
        "analysis_breakevens": "Σημεία εξισορρόπησης (Break-even)",
        "analysis_win_zone": "🟢 Κερδίζεις όταν",
        "analysis_lose_zone": "🔴 Χάνεις όταν",
        "analysis_net_cost": "Καθαρό κόστος",
        "analysis_scenario_case": "Αν η τιμή πάει…",
        "analysis_scenario_result": "Τότε…",
        "analysis_scenario_profit": "Κέρδος",
        "analysis_scenario_loss": "Ζημιά",
        "close": "Κλείσιμο",
        "unlimited": "Απεριόριστο",
    },
    "en": {
        "title": "📊 Options Dashboard",
        "subtitle": "Crypto + Stocks options dashboard",
        "symbol": "💰 Symbol:",
        "expiry": "📅 Expiry:",
        "presets": "⚡ Strategies (auto from spot):",
        "presets_hint": "👉 Automatic — picks strikes based on spot",
        "chain": "📋 Options Chain",
        "legs": "🎯 Strategy Legs",
        "all": "ALL", "calls": "CALLS", "puts": "PUTS",
        "long": "＋ LONG", "short": "－ SHORT",
        "manual_hint": "👉 Manual — uses the strikes you picked in the grid",
        "underlying": "＋ Underlying", "clear": "🗑️ Clear",
        "no_legs": "No legs yet — click a row for preview",
        "contracts": "contracts",
        "preset_cc": "🛡️ Covered Call",
        "preset_cs": "↗️ Call Spread",
        "preset_ic": "🦅 Iron Condor",
        "preset_st": "⚖️ Straddle",
        "about_btn": "❓ What is this?",
        "analysis_btn": "📊 Strategy Analysis",
        "guide_title": "📖 Strategy Guide",
        "analysis_title": "📊 Your Strategy Analysis",
        "analysis_no_legs": "⚠️ You haven't added any legs yet. Click a grid row and press **+ LONG** or **+ SHORT**, or pick a preset.",
        "analysis_your_legs": "🎯 Your legs",
        "analysis_chart": "📈 Profit / Loss Chart",
        "analysis_scenarios": "🎲 Scenarios — When you win and when you lose",
        "analysis_summary": "💰 Summary",
        "analysis_max_profit": "Max profit",
        "analysis_max_loss": "Max loss",
        "analysis_breakevens": "Break-even points",
        "analysis_win_zone": "🟢 You win when",
        "analysis_lose_zone": "🔴 You lose when",
        "analysis_net_cost": "Net cost",
        "analysis_scenario_case": "If price goes to…",
        "analysis_scenario_result": "Then…",
        "analysis_scenario_profit": "Profit",
        "analysis_scenario_loss": "Loss",
        "close": "Close",
        "unlimited": "Unlimited",
    },
}


THEMES = {
    "dark": {
        "bg": "#0e1117", "panel": "#161b22", "panel_alt": "#1c2128",
        "border": "#30363d", "text": "#e6edf3", "muted": "#8b949e",
        "grid_theme": "ag-theme-alpine-dark", "chart_bg": "#161b22",
        "btn_bg": "#21262d", "shadow": "0 2px 8px rgba(0,0,0,0.3)",
    },
    "light": {
        "bg": "#f6f8fa", "panel": "#ffffff", "panel_alt": "#f6f8fa",
        "border": "#d0d7de", "text": "#1f2328", "muted": "#57606a",
        "grid_theme": "ag-theme-alpine", "chart_bg": "#ffffff",
        "btn_bg": "#f6f8fa", "shadow": "0 2px 8px rgba(0,0,0,0.08)",
    },
}

PROFIT = "#2ecc71"
LOSS = "#e74c3c"
STRIKE = "#f39c12"
SPOT = "#58a6ff"
ACCENT = "#1f6feb"
RED = "#da3633"
CALL_COLOR = "#2ecc71"
PUT_COLOR = "#e74c3c"

CRYPTO_SYMBOLS = {"BTC", "ETH"}
ALL_SYMBOLS = ["BTC", "ETH", "AAPL", "SPY", "TSLA", "NVDA", "MSFT", "QQQ"]

_stock_session = curl_requests.Session(impersonate="chrome")
_stock_session.verify = False

_cache = {}


def cache_get(key):
    entry = _cache.get(key)
    if entry is None:
        return None
    value, expires = entry
    if time.time() > expires:
        del _cache[key]
        return None
    return value


def cache_set(key, value, ttl=300):
    _cache[key] = (value, time.time() + ttl)


def http_get(url, params=None, timeout=15):
    try:
        return requests.get(url, params=params, timeout=timeout)
    except requests.exceptions.SSLError:
        return requests.get(url, params=params, timeout=timeout, verify=False)


def get_crypto_expiries(currency="BTC"):
    key = f"expiries:{currency}"
    cached = cache_get(key)
    if cached is not None:
        return cached
    url = f"{DERIBIT}/public/get_instruments?currency={currency}&kind=option&expired=false"
    r = http_get(url)
    data = r.json().get("result", [])
    counts, labels = {}, {}
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
    matched = [i for i in data if marker in i.get("instrument_name", "")]

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
        bid_btc, ask_btc = item.get("bid_price"), item.get("ask_price")
        bid_usd = round(float(bid_btc) * spot, 2) if bid_btc and spot else None
        ask_usd = round(float(ask_btc) * spot, 2) if ask_btc and spot else None
        rows.append({
            "instrument": name, "type": opt_type, "strike": strike,
            "bid": bid_usd, "ask": ask_usd, "iv": item.get("mark_iv"),
            "delta": None, "volume": item.get("volume"), "oi": item.get("open_interest"),
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
        r = http_get(f"{DERIBIT}/public/get_index_price",
                     params={"index_name": index_name}, timeout=10)
        price = float(r.json()["result"]["index_price"])
        cache_set(key, price, ttl=30)
        return price
    except Exception:
        return None


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
        result = [(e, e) for e in expiries]
        cache_set(key, result, ttl=3600)
        return result
    except Exception:
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
    except Exception:
        return None


def _clean(v):
    try:
        if v is None:
            return 0.0
        f = float(v)
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
    except Exception:
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
    volume = _clean(r.get("volume"))
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
        "type": opt_type, "strike": strike, "bid": bid, "ask": ask,
        "iv": iv, "delta": None, "volume": int(volume),
        "oi": int(_clean(r.get("openInterest"))),
    }


# ============================================================
# ANALYSIS
# ============================================================
def analyze_strategy(spot, legs, lang):
    if not legs:
        return None
    s = STRINGS[lang]

    strikes = [l["strike"] for l in legs if l["type"] != "underlying"]
    all_levels = strikes + [spot] if strikes else [spot]
    low = min(all_levels) * 0.80
    high = max(all_levels) * 1.20
    step = (high - low) / 200
    prices = [low + i * step for i in range(201)]

    def payoff(p):
        pnl = 0.0
        for leg in legs:
            side = leg["side"]
            prem = leg["premium"]
            if leg["type"] == "underlying":
                pnl += side * (p - spot)
            elif leg["type"] == "call":
                pnl += side * (max(p - leg["strike"], 0) - prem)
            elif leg["type"] == "put":
                pnl += side * (max(leg["strike"] - p, 0) - prem)
        return pnl

    pnls = [payoff(p) for p in prices]

    net_cost = 0.0
    for leg in legs:
        if leg["type"] == "underlying":
            continue
        net_cost += -1 * leg["side"] * leg["premium"]

    breakevens = []
    for i in range(1, len(prices)):
        if pnls[i-1] * pnls[i] < 0:
            x0, y0 = prices[i-1], pnls[i-1]
            x1, y1 = prices[i], pnls[i]
            if y1 != y0:
                xcross = x0 - y0 * (x1 - x0) / (y1 - y0)
                breakevens.append(round(xcross, 2))

    max_profit = max(pnls)
    max_loss = min(pnls)

    profit_unlimited = False
    loss_unlimited = False
    if len(pnls) >= 20:
        slope_high = pnls[-1] - pnls[-10]
        if slope_high > 100:
            profit_unlimited = True
        slope_low = pnls[10] - pnls[0]
        if slope_low > 100:
            profit_unlimited = True

    win_ranges = []
    in_win = False
    win_start = None
    for i, pnl in enumerate(pnls):
        if pnl > 0 and not in_win:
            in_win = True
            win_start = prices[i]
        elif pnl <= 0 and in_win:
            in_win = False
            win_ranges.append((round(win_start, 2), round(prices[i-1], 2)))
    if in_win:
        win_ranges.append((round(win_start, 2), round(prices[-1], 2)))

    scenarios = []
    test_prices = sorted(set([
        round(spot * 0.90, 2), round(spot * 0.95, 2),
        round(spot, 2),
        round(spot * 1.05, 2), round(spot * 1.10, 2), round(spot * 1.15, 2),
    ]))
    while len(test_prices) < 6:
        test_prices.append(round(test_prices[-1] * 1.05, 2))
    test_prices = test_prices[:6]

    for p in test_prices:
        pnl = payoff(p)
        scenarios.append({"price": p, "pnl": round(pnl, 2), "is_profit": pnl >= 0})

    # Chart
    fig = go.Figure()
    profit_x, profit_y = [], []
    loss_x, loss_y = [], []
    for x, y in zip(prices, pnls):
        if y >= 0:
            profit_x.append(x); profit_y.append(y)
        else:
            loss_x.append(x); loss_y.append(y)

    fig.add_trace(go.Scatter(x=profit_x, y=profit_y, mode="lines",
                             line=dict(color=PROFIT, width=3),
                             fill="tozeroy", fillcolor="rgba(46, 204, 113, 0.25)"))
    fig.add_trace(go.Scatter(x=loss_x, y=loss_y, mode="lines",
                             line=dict(color=LOSS, width=3),
                             fill="tozeroy", fillcolor="rgba(231, 76, 60, 0.25)"))

    fig.add_hline(y=0, line_dash="dash", line_color="#8b949e")
    fig.add_vline(x=spot, line_dash="dot", line_color=SPOT, line_width=2,
                  annotation_text=f"Spot ${spot:,.0f}", annotation_position="top",
                  annotation_font=dict(color=SPOT, size=11))

    for k in sorted(set(strikes)):
        fig.add_vline(x=k, line_dash="dot", line_color=STRIKE, line_width=1,
                      annotation_text=f"K={k:,.0f}", annotation_position="bottom",
                      annotation_font=dict(color=STRIKE, size=9))
    for be in breakevens:
        fig.add_vline(x=be, line_dash="dot", line_color="#f39c12", line_width=1,
                      annotation_text=f"BE ${be:,.0f}", annotation_position="top right",
                      annotation_font=dict(color=STRIKE, size=10))

    fig.update_layout(
        paper_bgcolor="#161b22", plot_bgcolor="#161b22",
        font=dict(color="#e6edf3", size=11),
        xaxis=dict(title=dict(text="Price at Expiry", font=dict(color="#e6edf3")),
                   tickfont=dict(color="#8b949e"), gridcolor="#30363d"),
        yaxis=dict(title=dict(text="P&L ($)", font=dict(color="#e6edf3")),
                   tickfont=dict(color="#8b949e"), gridcolor="#30363d"),
        margin=dict(l=60, r=30, t=30, b=50),
        showlegend=False, height=320,
    )

    return {
        "chart": fig, "scenarios": scenarios,
        "net_cost": round(net_cost, 2),
        "max_profit": max_profit, "max_loss": max_loss,
        "profit_unlimited": profit_unlimited,
        "loss_unlimited": loss_unlimited,
        "breakevens": breakevens, "win_ranges": win_ranges,
        "spot": spot, "legs": legs,
    }


def make_multi_leg_chart(spot, legs, symbol, theme="dark"):
    t = THEMES[theme]
    if not legs:
        fig = go.Figure()
        fig.update_layout(
            paper_bgcolor=t["chart_bg"], plot_bgcolor=t["chart_bg"],
            font=dict(color=t["text"]),
            annotations=[dict(text="Add legs or pick a preset",
                              x=0.5, y=0.5, xref="paper", yref="paper",
                              showarrow=False, font=dict(color=t["muted"], size=14))],
        )
        return fig
    analysis = analyze_strategy(spot, legs, "en")
    if analysis:
        return analysis["chart"]
    return go.Figure()


def make_preview_chart(spot, strike, premium, symbol, theme="dark"):
    t = THEMES[theme]
    low = min(spot, strike) * 0.85
    high = max(spot, strike) * 1.15
    step = (high - low) / 60
    prices = [low + i * step for i in range(61)]
    payoffs = []
    for p in prices:
        if p <= strike:
            payoffs.append((p - spot) + premium)
        else:
            payoffs.append((strike - spot) + premium)
    fig = go.Figure()
    profit_x, profit_y = [], []
    loss_x, loss_y = [], []
    for x, y in zip(prices, payoffs):
        if y >= 0:
            profit_x.append(x); profit_y.append(y)
        else:
            loss_x.append(x); loss_y.append(y)
    fig.add_trace(go.Scatter(x=profit_x, y=profit_y, mode="lines",
                             line=dict(color=PROFIT, width=3),
                             fill="tozeroy", fillcolor="rgba(46, 204, 113, 0.20)"))
    fig.add_trace(go.Scatter(x=loss_x, y=loss_y, mode="lines",
                             line=dict(color=LOSS, width=3),
                             fill="tozeroy", fillcolor="rgba(231, 76, 60, 0.20)"))
    fig.add_hline(y=0, line_dash="dash", line_color=t["muted"])
    fig.add_vline(x=strike, line_dash="dot", line_color=STRIKE,
                  annotation_text=f"Strike {strike}", annotation_position="top right",
                  annotation_font=dict(color=STRIKE, size=12))
    fig.add_vline(x=spot, line_dash="dot", line_color=SPOT,
                  annotation_text=f"Spot {round(spot, 2)}", annotation_position="bottom left",
                  annotation_font=dict(color=SPOT, size=11))
    fig.update_layout(
        title=dict(text=f"<b>Covered Call Preview — {symbol}</b>",
                   font=dict(color=t["text"], size=16), x=0.02),
        xaxis=dict(title=dict(text=f"{symbol} Price at Expiry", font=dict(color=t["text"])),
                   tickfont=dict(color=t["muted"]), gridcolor=t["border"], zerolinecolor=t["border"]),
        yaxis=dict(title=dict(text="Profit / Loss ($)", font=dict(color=t["text"])),
                   tickfont=dict(color=t["muted"]), gridcolor=t["border"], zerolinecolor=t["border"]),
        paper_bgcolor=t["chart_bg"], plot_bgcolor=t["chart_bg"],
        font=dict(color=t["text"]),
        hovermode="x unified", margin=dict(l=60, r=30, t=80, b=50), showlegend=False,
    )
    return fig


app = Dash(__name__)
server = app.server


app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Options Dashboard v2</title>
        {%favicon%}
        {%css%}
        <style>
            * { box-sizing: border-box; }
            body { margin: 0; }

            .ds-btn, .ds-symbol, .ds-expiry, .ds-preset, .ds-action, .ds-filter, .ds-theme {
                font-family: inherit;
                cursor: pointer;
                transition: all 0.15s ease;
                display: inline-flex;
                align-items: center;
                gap: 5px;
                white-space: nowrap;
            }
            .ds-btn:hover, .ds-symbol:hover, .ds-expiry:hover,
            .ds-preset:hover, .ds-action:hover, .ds-filter:hover {
                transform: translateY(-1px);
                filter: brightness(1.15);
            }
            .ds-symbol { padding: 9px 16px; margin-right: 6px; margin-bottom: 6px;
                border-radius: 8px; font-size: 13px; font-weight: 600; letter-spacing: 0.3px; }
            .ds-expiry { padding: 7px 12px; margin-right: 6px; margin-bottom: 6px;
                border-radius: 7px; font-size: 11px; font-weight: 600; }
            .ds-preset { padding: 9px 14px; margin-right: 8px; margin-bottom: 6px;
                border-radius: 8px; font-size: 12px; font-weight: 600; letter-spacing: 0.3px; }
            .ds-action { padding: 6px 12px; margin-left: 6px;
                border-radius: 7px; font-size: 11px; font-weight: 700; letter-spacing: 0.5px; }
            .ds-filter { padding: 6px 12px; margin-left: 6px;
                border-radius: 7px; font-size: 11px; font-weight: 700; letter-spacing: 0.5px; }
            .ds-theme { font-size: 18px; padding: 8px 14px; border-radius: 10px; }
            .ds-theme:hover { transform: rotate(15deg) scale(1.1);
                box-shadow: 0 4px 14px rgba(243, 156, 18, 0.4); }

            .ag-theme-alpine-dark {
                --ag-background-color: #161b22;
                --ag-header-background-color: #1c2128;
                --ag-odd-row-background-color: #161b22;
                --ag-even-row-background-color: #1a1f27;
                --ag-row-hover-color: #21262d;
                --ag-border-color: #30363d;
                --ag-foreground-color: #e6edf3;
                --ag-header-foreground-color: #e6edf3;
                --ag-selected-row-background-color: #1f6feb;
            }
            .ag-theme-alpine {
                --ag-background-color: #ffffff;
                --ag-header-background-color: #f6f8fa;
                --ag-odd-row-background-color: #ffffff;
                --ag-even-row-background-color: #fafbfc;
                --ag-row-hover-color: #f3f4f6;
                --ag-border-color: #d0d7de;
                --ag-foreground-color: #1f2328;
                --ag-header-foreground-color: #1f2328;
                --ag-selected-row-background-color: #dbeafe;
            }

            .ds-hint {
                font-size: 11px;
                color: #8b949e;
                font-style: italic;
                margin-left: 8px;
                padding: 2px 8px;
                border-left: 2px solid #30363d;
            }

            @media (max-width: 1000px) {
                #main-grid { grid-template-columns: 1fr !important; }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""


app.layout = html.Div([
    html.Div([
        html.Div([
            html.H1(id="app-title",
                    style={"margin": "0", "fontSize": "22px", "fontWeight": "700"}),
            html.P(id="app-subtitle",
                   style={"margin": "4px 0 0 0", "fontSize": "12px"}),
        ], style={"flex": "1"}),
        html.Button("🇬🇷 / 🇬🇧", id="lang-toggle", n_clicks=0, className="ds-theme"),
        html.Button("☀️", id="theme-toggle", n_clicks=0, className="ds-theme",
                    style={"marginLeft": "8px"}),
        html.Button(id="about-btn", n_clicks=0, className="ds-preset",
                    style={"marginLeft": "12px"}),
        html.Button(id="analysis-btn", n_clicks=0, className="ds-preset",
                    style={"marginLeft": "8px"}),
    ], id="header", style={"display": "flex", "alignItems": "center", "padding": "16px 24px"}),

    html.Div([
        html.Span(id="symbol-label",
                  style={"marginRight": "12px", "fontSize": "13px", "fontWeight": "700"}),
        html.Div(id="symbol-buttons", style={"display": "inline-block"}),
    ], id="symbol-row", style={"display": "flex", "alignItems": "center",
                                "padding": "12px 24px 0 24px", "flexWrap": "wrap"}),

    html.Div([
        html.Span(id="expiry-label",
                  style={"marginRight": "12px", "fontSize": "13px", "fontWeight": "700"}),
        html.Div(id="expiry-buttons", style={"display": "inline-flex", "flexWrap": "wrap"}),
    ], id="expiry-row", style={"display": "flex", "alignItems": "center",
                                "padding": "12px 24px", "flexWrap": "wrap"}),

    html.Div([
        html.Span(id="presets-label",
                  style={"marginRight": "12px", "fontSize": "13px", "fontWeight": "700"}),
        html.Button(id="preset-cc", n_clicks=0, className="ds-preset"),
        html.Button(id="preset-cs", n_clicks=0, className="ds-preset"),
        html.Button(id="preset-ic", n_clicks=0, className="ds-preset"),
        html.Button(id="preset-st", n_clicks=0, className="ds-preset"),
        html.Span(id="presets-hint", className="ds-hint"),
    ], id="preset-row", style={"display": "flex", "alignItems": "center",
                                "padding": "0 24px 12px 24px", "flexWrap": "wrap"}),

    html.Div([
        html.Div([
            html.Div([
                html.Span(id="chain-label",
                          style={"fontWeight": "700", "fontSize": "14px"}),
                html.Span(id="row-count",
                          style={"fontSize": "12px", "marginLeft": "8px"}),
                html.Div([
                    html.Button(id={"type": "filter-btn", "value": "all"}, n_clicks=0, className="ds-filter"),
                    html.Button(id={"type": "filter-btn", "value": "call"}, n_clicks=0, className="ds-filter"),
                    html.Button(id={"type": "filter-btn", "value": "put"}, n_clicks=0, className="ds-filter"),
                ], id="filter-row", style={"display": "inline-block", "marginLeft": "16px"}),
            ], id="grid-header", style={"padding": "12px 16px"}),

            # Manual actions row (below the filter buttons)
            html.Div([
                html.Div([
                    html.Button(id="add-long-btn", n_clicks=0, className="ds-action"),
                    html.Button(id="add-short-btn", n_clicks=0, className="ds-action"),
                    html.Span(id="manual-hint", className="ds-hint"),
                ], style={"display": "flex", "alignItems": "center"}),
            ], id="manual-row", style={"padding": "0 16px 12px 16px"}),

            dag.AgGrid(
                id="chain-grid",
                columnDefs=[
                    {"field": "instrument", "headerName": "Instrument", "flex": 2, "minWidth": 200},
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
                    {"field": "volume", "headerName": "Vol", "flex": 1,
                     "valueFormatter": {"function": "params.value != null ? Number(params.value).toLocaleString() : ''"}},
                    {"field": "oi", "headerName": "OI", "flex": 1,
                     "valueFormatter": {"function": "params.value != null ? Number(params.value).toLocaleString() : ''"}},
                ],
                rowData=[],
                style={"height": "calc(100vh - 460px)", "minHeight": "280px"},
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
                    html.Span(id="legs-label",
                              style={"fontWeight": "700", "fontSize": "13px"}),
                    html.Button(id="add-underlying-btn", n_clicks=0, className="ds-action"),
                    html.Button(id="clear-legs-btn", n_clicks=0, className="ds-action"),
                ], style={"marginBottom": "8px"}),
                html.Div(id="legs-list",
                         children=html.Span("No legs yet — click a row for preview",
                                            style={"fontSize": "12px"})),
            ], id="legs-panel", style={"padding": "12px 16px", "minHeight": "100px",
                                        "maxHeight": "180px", "overflowY": "auto"}),
        ], id="grid-panel", style={"borderRadius": "8px", "overflow": "hidden"}),

        html.Div([
            dcc.Graph(id="chart", style={"height": "calc(100vh - 260px)", "minHeight": "400px"},
                      config={"displayModeBar": False}),
        ], id="chart-panel", style={"borderRadius": "8px", "overflow": "hidden"}),
    ], id="main-grid", style={"display": "grid", "gridTemplateColumns": "1fr 1fr",
                               "gap": "16px", "padding": "16px 24px"}),

    html.Div([
        html.Div([
            html.Div([
                html.Span(id="about-title",
                          style={"fontWeight": "700", "fontSize": "16px"}),
                html.Button("✕", id="close-about-btn", n_clicks=0,
                            style={"padding": "4px 10px", "borderRadius": "5px",
                                   "border": "1px solid #30363d", "background": "transparent",
                                   "color": "#e6edf3", "fontSize": "14px", "cursor": "pointer"}),
            ], style={"display": "flex", "justifyContent": "space-between",
                      "alignItems": "center", "marginBottom": "12px"}),
            dcc.Markdown(id="about-body", style={"fontSize": "13px", "lineHeight": "1.6"}),
        ], id="about-content", style={}),
    ], id="about-modal", style={"display": "none"}),

    html.Div([
        html.Div([
            html.Div([
                html.Span(id="analysis-title",
                          style={"fontWeight": "700", "fontSize": "16px"}),
                html.Button("✕", id="close-analysis-btn", n_clicks=0,
                            style={"padding": "4px 10px", "borderRadius": "5px",
                                   "border": "1px solid #30363d", "background": "transparent",
                                   "color": "#e6edf3", "fontSize": "14px", "cursor": "pointer"}),
            ], style={"display": "flex", "justifyContent": "space-between",
                      "alignItems": "center", "marginBottom": "12px"}),
            html.Div(id="analysis-body"),
        ], id="analysis-content", style={}),
    ], id="analysis-modal", style={"display": "none"}),

    dcc.Interval(id="tick", interval=30000, n_intervals=0),
    dcc.Store(id="theme-store", data="dark"),
    dcc.Store(id="lang-store", data="el"),
    dcc.Store(id="symbol-store", data="BTC"),
    dcc.Store(id="expiry-store", data=None),
    dcc.Store(id="expiry-list", data=[]),
    dcc.Store(id="legs-store", data=[]),
    dcc.Store(id="filter-store", data="all"),
    dcc.Store(id="rows-store", data=[]),
    dcc.Store(id="about-open", data=False),
    dcc.Store(id="analysis-open", data=False),
], id="root", style={
    "minHeight": "100vh",
    "fontFamily": "Inter, -apple-system, Segoe UI, sans-serif",
    "background": THEMES["dark"]["bg"], "color": THEMES["dark"]["text"],
})


# CALLBACKS
@callback(Output("theme-store", "data"),
          Input("theme-toggle", "n_clicks"),
          State("theme-store", "data"), prevent_initial_call=True)
def toggle_theme(n, current):
    return "light" if current == "dark" else "dark"


@callback(Output("lang-store", "data"),
          Input("lang-toggle", "n_clicks"),
          State("lang-store", "data"), prevent_initial_call=True)
def toggle_lang(n, current):
    return "en" if current == "el" else "el"


@callback(Output("about-open", "data"),
          Input("about-btn", "n_clicks"),
          Input("close-about-btn", "n_clicks"),
          State("about-open", "data"), prevent_initial_call=True)
def toggle_about(n1, n2, current):
    return ctx.triggered_id == "about-btn"


@callback(Output("analysis-open", "data"),
          Input("analysis-btn", "n_clicks"),
          Input("close-analysis-btn", "n_clicks"),
          State("analysis-open", "data"), prevent_initial_call=True)
def toggle_analysis(n1, n2, current):
    return ctx.triggered_id == "analysis-btn"


@callback(
    Output("app-title", "children"),
    Output("app-subtitle", "children"),
    Output("symbol-label", "children"),
    Output("expiry-label", "children"),
    Output("presets-label", "children"),
    Output("presets-hint", "children"),
    Output("chain-label", "children"),
    Output("legs-label", "children"),
    Output("add-long-btn", "children"),
    Output("add-short-btn", "children"),
    Output("manual-hint", "children"),
    Output("add-underlying-btn", "children"),
    Output("clear-legs-btn", "children"),
    Output("preset-cc", "children"),
    Output("preset-cs", "children"),
    Output("preset-ic", "children"),
    Output("preset-st", "children"),
    Output("about-btn", "children"),
    Output("analysis-btn", "children"),
    Output("about-title", "children"),
    Input("lang-store", "data"),
)
def render_language(lang):
    s = STRINGS[lang]
    return (
        s["title"], s["subtitle"], s["symbol"], s["expiry"], s["presets"],
        s["presets_hint"],
        s["chain"], s["legs"], s["long"], s["short"], s["manual_hint"],
        s["underlying"], s["clear"],
        s["preset_cc"], s["preset_cs"], s["preset_ic"], s["preset_st"],
        s["about_btn"], s["analysis_btn"], s["guide_title"],
    )


@callback(
    Output("about-modal", "style"),
    Output("about-content", "style"),
    Output("about-title", "style"),
    Output("about-body", "children"),
    Input("about-open", "data"),
    Input("theme-store", "data"),
    Input("lang-store", "data"),
)
def render_about_modal(is_open, theme, lang):
    t = THEMES[theme]
    if is_open:
        modal_style = {"display": "flex", "position": "fixed", "top": "0", "left": "0",
                       "width": "100%", "height": "100%",
                       "background": "rgba(0,0,0,0.7)",
                       "justifyContent": "center", "alignItems": "center", "zIndex": "9999"}
    else:
        modal_style = {"display": "none"}
    content_style = {"background": t["panel"], "border": f"1px solid {t['border']}",
                     "borderRadius": "12px", "padding": "24px",
                     "maxWidth": "750px", "width": "90%", "maxHeight": "85vh",
                     "overflowY": "auto", "color": t["text"]}
    title_style = {"fontWeight": "700", "fontSize": "16px", "color": t["text"]}

    if lang == "el":
        body = """
### 🛡️ Covered Call
Αγοράζεις το υποκείμενο, πουλάς ένα OTM call. Μικρό σταθερό κέρδος σε flat αγορές.

### ↗️ Call Spread
Αγοράζεις call + πουλάς call πιο ψηλά. Περιορισμένο κέρδος, μικρό κόστος.

### 🦅 Iron Condor
4 legs. Κερδίζεις αν η τιμή μείνει κοντά στο spot.

### ⚖️ Straddle
Αγοράζεις call + put στο ίδιο strike. Κερδίζεις αν κουνηθεί πολύ.

---
💡 **Για πραγματικά νούμερα**, πρόσθεσε legs και πάτα **📊 Ανάλυση Στρατηγικής**.

**Δύο τρόποι για να χτίσεις στρατηγική:**
- **⚡ Presets (auto):** επιλέγουν strikes **αυτόματα με βάση το spot**.
- **＋ LONG / － SHORT (manual):** χρησιμοποιούν **τη γραμμή που διάλεξες** στο grid.
"""
    else:
        body = """
### 🛡️ Covered Call
Buy underlying, sell OTM call. Small steady profit in flat markets.

### ↗️ Call Spread
Buy call + sell higher call. Capped profit, low cost.

### 🦅 Iron Condor
4 legs. Win if price stays near spot.

### ⚖️ Straddle
Buy call + put at same strike. Win if price moves a lot.

---
💡 **For real numbers**, add legs and press **📊 Strategy Analysis**.

**Two ways to build a strategy:**
- **⚡ Presets (auto):** pick strikes **automatically based on spot**.
- **＋ LONG / － SHORT (manual):** use **the row you selected** in the grid.
"""
    return modal_style, content_style, title_style, body


@callback(
    Output("analysis-modal", "style"),
    Output("analysis-content", "style"),
    Output("analysis-title", "style"),
    Output("analysis-body", "children"),
    Input("analysis-open", "data"),
    Input("legs-store", "data"),
    Input("theme-store", "data"),
    Input("lang-store", "data"),
    State("symbol-store", "data"),
)
def render_analysis_modal(is_open, legs, theme, lang, symbol):
    t = THEMES[theme]
    s = STRINGS[lang]
    if is_open:
        modal_style = {"display": "flex", "position": "fixed", "top": "0", "left": "0",
                       "width": "100%", "height": "100%",
                       "background": "rgba(0,0,0,0.75)",
                       "justifyContent": "center", "alignItems": "center",
                       "zIndex": "9999", "padding": "20px"}
    else:
        modal_style = {"display": "none"}
    content_style = {"background": t["panel"], "border": f"1px solid {t['border']}",
                     "borderRadius": "12px", "padding": "24px",
                     "maxWidth": "900px", "width": "95%", "maxHeight": "90vh",
                     "overflowY": "auto", "color": t["text"]}
    title_style = {"fontWeight": "700", "fontSize": "16px", "color": t["text"]}

    if not legs:
        return (modal_style, content_style, title_style,
                html.Div(s["analysis_no_legs"],
                         style={"padding": "20px", "fontSize": "14px", "color": t["muted"]}))

    symbol = symbol or "BTC"
    if symbol in CRYPTO_SYMBOLS:
        spot = get_crypto_spot(symbol) or 100
    else:
        spot = get_stock_spot(symbol) or 100

    analysis = analyze_strategy(spot, legs, lang)
    if not analysis:
        return (modal_style, content_style, title_style,
                html.Div("Error", style={"padding": "20px"}))

    body_children = []
    body_children.append(html.H3(s["analysis_your_legs"],
                                 style={"fontSize": "15px", "marginTop": "0"}))
    leg_items = []
    for i, leg in enumerate(legs):
        side_color = PROFIT if leg["side"] > 0 else RED
        side_text = "LONG" if leg["side"] > 0 else "SHORT"
        if leg["type"] == "underlying":
            detail = f"{leg['instrument']} @ ${spot:,.2f}"
        else:
            detail = f"{leg['type'].upper()} K=${leg['strike']:,.2f} @ ${leg['premium']:,.2f}"
        leg_items.append(html.Div([
            html.Span(f"#{i+1} ", style={"color": t["muted"], "fontSize": "11px"}),
            html.Span(f"{side_text} ", style={"color": side_color, "fontWeight": "700", "fontSize": "13px"}),
            html.Span(detail, style={"color": t["text"], "fontSize": "13px"}),
        ], style={"padding": "4px 0", "borderBottom": f"1px solid {t['border']}"}))
    body_children.append(html.Div(leg_items, style={"marginBottom": "20px"}))

    body_children.append(html.H3(s["analysis_summary"], style={"fontSize": "15px"}))
    net_cost = analysis["net_cost"]
    cost_color = RED if net_cost > 0 else PROFIT
    cost_label = f"${net_cost:,.2f}" if abs(net_cost) >= 0.01 else "$0"

    max_p = analysis["max_profit"]
    max_l = analysis["max_loss"]
    p_str = s["unlimited"] if analysis["profit_unlimited"] else f"${max_p:,.2f}"
    l_str = s["unlimited"] if analysis["loss_unlimited"] else f"${max_l:,.2f}"

    summary = html.Div([
        html.Div([html.Span(s["analysis_net_cost"] + ": ", style={"fontWeight": "600"}),
                  html.Span(cost_label, style={"color": cost_color, "fontWeight": "700"})],
                 style={"marginBottom": "6px"}),
        html.Div([html.Span(s["analysis_max_profit"] + ": ", style={"fontWeight": "600"}),
                  html.Span(p_str, style={"color": PROFIT, "fontWeight": "700"})],
                 style={"marginBottom": "6px"}),
        html.Div([html.Span(s["analysis_max_loss"] + ": ", style={"fontWeight": "600"}),
                  html.Span(l_str, style={"color": LOSS, "fontWeight": "700"})],
                 style={"marginBottom": "6px"}),
    ], style={"background": t["panel_alt"], "padding": "12px 16px",
              "borderRadius": "8px", "marginBottom": "20px"})

    win_ranges = analysis["win_ranges"]
    if win_ranges:
        win_text = " or ".join([f"${a:,.0f} – ${b:,.0f}" for a, b in win_ranges])
        summary.children.append(html.Div([
            html.Span(s["analysis_win_zone"] + ": ", style={"fontWeight": "600"}),
            html.Span(win_text, style={"color": PROFIT, "fontWeight": "700"}),
        ], style={"marginBottom": "6px"}))
        lose_text = ""
        if len(win_ranges) == 1:
            a, b = win_ranges[0]
            lose_text = f"< ${a:,.0f} or > ${b:,.0f}"
        summary.children.append(html.Div([
            html.Span(s["analysis_lose_zone"] + ": ", style={"fontWeight": "600"}),
            html.Span(lose_text, style={"color": LOSS, "fontWeight": "700"}),
        ], style={"marginBottom": "6px"}))

    body_children.append(summary)

    bes = analysis["breakevens"]
    if bes:
        body_children.append(html.H3(s["analysis_breakevens"], style={"fontSize": "15px"}))
        be_items = [html.Span(f"${be:,.2f}",
                              style={"background": t["panel_alt"], "padding": "4px 10px",
                                     "borderRadius": "6px", "marginRight": "8px",
                                     "display": "inline-block", "marginBottom": "8px",
                                     "border": f"1px solid {STRIKE}",
                                     "color": STRIKE, "fontWeight": "600", "fontSize": "13px"})
                    for be in bes]
        body_children.append(html.Div(be_items, style={"marginBottom": "20px"}))

    body_children.append(html.H3(s["analysis_chart"], style={"fontSize": "15px"}))
    body_children.append(dcc.Graph(figure=analysis["chart"],
                                   config={"displayModeBar": False},
                                   style={"marginBottom": "20px", "height": "320px"}))

    body_children.append(html.H3(s["analysis_scenarios"], style={"fontSize": "15px"}))
    scenario_rows = []
    for sc in analysis["scenarios"]:
        is_profit = sc["is_profit"]
        result_color = PROFIT if is_profit else LOSS
        result_text = (f"{s['analysis_scenario_profit']}: " if is_profit
                       else f"{s['analysis_scenario_loss']}: ")
        scenario_rows.append(html.Div([
            html.Span(f"{s['analysis_scenario_case']} ", style={"color": t["muted"]}),
            html.Span(f"${sc['price']:,.0f}", style={"fontWeight": "700", "color": t["text"]}),
            html.Span(f" → {result_text}", style={"color": t["muted"]}),
            html.Span(f"${abs(sc['pnl']):,.2f}",
                      style={"color": result_color, "fontWeight": "700"}),
        ], style={"padding": "8px 12px", "borderBottom": f"1px solid {t['border']}",
                  "fontSize": "13px"}))

    body_children.append(html.Div(scenario_rows, style={
        "background": t["panel_alt"], "borderRadius": "8px", "overflow": "hidden"}))

    return modal_style, content_style, title_style, body_children


@callback(Output("symbol-buttons", "children"),
          Input("symbol-store", "data"),
          Input("theme-store", "data"))
def render_symbol_buttons(active, theme):
    t = THEMES[theme]
    buttons = []
    icons = {"BTC": "₿", "ETH": "Ξ", "AAPL": "", "SPY": "📈", "TSLA": "🚗",
             "NVDA": "🎮", "MSFT": "🪟", "QQQ": "📊"}
    for sym in ALL_SYMBOLS:
        is_active = (sym == active)
        icon = icons.get(sym, "")
        label = f"{icon} {sym}" if icon else sym
        if is_active:
            style = {"background": f"linear-gradient(135deg, {ACCENT} 0%, #4a8fe7 100%)",
                     "color": "#ffffff", "border": f"1px solid {ACCENT}",
                     "boxShadow": f"0 4px 14px {ACCENT}66", "fontWeight": "700"}
        else:
            style = {"background": t["btn_bg"], "color": t["text"],
                     "border": f"1px solid {t['border']}"}
        buttons.append(html.Button(label,
                                   id={"type": "symbol-btn", "value": sym},
                                   n_clicks=0, className="ds-symbol", style=style))
    return buttons


@callback(Output("symbol-store", "data", allow_duplicate=True),
          Input({"type": "symbol-btn", "value": dash_all}, "n_clicks"),
          prevent_initial_call=True)
def on_symbol_click(_):
    return ctx.triggered_id["value"] if ctx.triggered_id else no_update


@callback(Output("filter-store", "data"),
          Input({"type": "filter-btn", "value": dash_all}, "n_clicks"),
          prevent_initial_call=True)
def on_filter_click(_):
    return ctx.triggered_id["value"] if ctx.triggered_id else no_update


@callback(Output("expiry-list", "data"),
          Output("expiry-store", "data", allow_duplicate=True),
          Input("symbol-store", "data"),
          prevent_initial_call="initial_duplicate")
def load_expiries_for_symbol(symbol):
    if not symbol:
        return [], None
    try:
        if symbol in CRYPTO_SYMBOLS:
            expiries = get_crypto_expiries(currency=symbol)
            data = [[ts, label] for ts, label in expiries[:12]]
            default = expiries[0][1] if expiries else None
        else:
            expiries = get_stock_expiries(symbol)
            data = [[label, label] for ts, label in expiries[:12]]
            default = expiries[0][1] if expiries else None
    except Exception:
        return [], None
    return data, default


@callback(Output("expiry-buttons", "children"),
          Input("expiry-list", "data"),
          Input("expiry-store", "data"),
          Input("theme-store", "data"))
def render_expiry_buttons(expiry_list, active, theme):
    t = THEMES[theme]
    if not expiry_list:
        return html.Span("Loading…", style={"fontSize": "12px", "color": t["muted"]})
    buttons = []
    for ts, label in expiry_list:
        is_active = (str(label) == str(active))
        if is_active:
            style = {"background": f"linear-gradient(135deg, {ACCENT} 0%, #4a8fe7 100%)",
                     "color": "#ffffff", "border": f"1px solid {ACCENT}",
                     "boxShadow": f"0 3px 10px {ACCENT}55", "fontWeight": "700"}
        else:
            style = {"background": t["btn_bg"], "color": t["text"],
                     "border": f"1px solid {t['border']}"}
        buttons.append(html.Button(label,
                                   id={"type": "expiry-btn", "value": str(label)},
                                   n_clicks=0, className="ds-expiry", style=style))
    return buttons


@callback(Output("expiry-store", "data", allow_duplicate=True),
          Input({"type": "expiry-btn", "value": dash_all}, "n_clicks"),
          prevent_initial_call=True)
def on_expiry_click(_):
    return ctx.triggered_id["value"] if ctx.triggered_id else no_update


@callback(Output({"type": "filter-btn", "value": dash_all}, "children"),
          Output({"type": "filter-btn", "value": dash_all}, "style"),
          Input("lang-store", "data"),
          Input("filter-store", "data"),
          State({"type": "filter-btn", "value": dash_all}, "value"),
          prevent_initial_call=False)
def render_filter_buttons(lang, active, _):
    s = STRINGS[lang]
    labels = {"all": s["all"], "call": s["calls"], "put": s["puts"]}
    children, styles = [], []
    for value in ["all", "call", "put"]:
        is_active = (value == active)
        children.append(labels[value])
        if value == "all":
            color = "#ffffff"
        elif value == "call":
            color = CALL_COLOR
        else:
            color = PUT_COLOR
        if is_active:
            styles.append({"background": f"linear-gradient(135deg, {ACCENT} 0%, #4a8fe7 100%)",
                           "color": "#ffffff", "border": f"1px solid {ACCENT}",
                           "boxShadow": f"0 3px 10px {ACCENT}55"})
        else:
            styles.append({"background": "transparent", "color": color,
                           "border": f"1px solid {color}"})
    return children, styles


@callback(Output("rows-store", "data"),
          Input("tick", "n_intervals"),
          Input("symbol-store", "data"),
          Input("expiry-store", "data"),
          State("expiry-list", "data"),
          prevent_initial_call=True)
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


@callback(Output("chain-grid", "rowData"),
          Output("row-count", "children"),
          Output("chain-grid", "selectedRows", allow_duplicate=True),
          Input("rows-store", "data"),
          Input("filter-store", "data"),
          Input("lang-store", "data"),
          State("chain-grid", "selectedRows"),
          prevent_initial_call=True)
def apply_filter(rows, filter_value, lang, current_selected):
    s = STRINGS[lang]
    if not rows:
        return [], f"0 {s['contracts']}", no_update
    if filter_value == "call":
        filtered = [r for r in rows if r["type"] == "call"]
    elif filter_value == "put":
        filtered = [r for r in rows if r["type"] == "put"]
    else:
        filtered = rows
    selected = current_selected
    if not selected and filtered:
        selected = [filtered[0]]
    return filtered, f"{len(filtered)} {s['contracts']}", selected


@callback(Output("legs-store", "data", allow_duplicate=True),
          Input("add-long-btn", "n_clicks"),
          State("chain-grid", "selectedRows"),
          State("legs-store", "data"), prevent_initial_call=True)
def add_long(n, selected, legs):
    if not selected or n == 0:
        return legs
    row = selected[0]
    leg = {"side": 1, "type": row["type"], "strike": row["strike"],
           "premium": row.get("bid") or 0, "instrument": row["instrument"]}
    return (legs or []) + [leg]


@callback(Output("legs-store", "data", allow_duplicate=True),
          Input("add-short-btn", "n_clicks"),
          State("chain-grid", "selectedRows"),
          State("legs-store", "data"), prevent_initial_call=True)
def add_short(n, selected, legs):
    if not selected or n == 0:
        return legs
    row = selected[0]
    leg = {"side": -1, "type": row["type"], "strike": row["strike"],
           "premium": row.get("bid") or 0, "instrument": row["instrument"]}
    return (legs or []) + [leg]


@callback(Output("legs-store", "data", allow_duplicate=True),
          Input("add-underlying-btn", "n_clicks"),
          State("symbol-store", "data"),
          State("legs-store", "data"), prevent_initial_call=True)
def add_underlying(n, symbol, legs):
    if n == 0:
        return legs
    leg = {"side": 1, "type": "underlying", "strike": 0, "premium": 0,
           "instrument": symbol}
    return (legs or []) + [leg]


@callback(Output("legs-store", "data", allow_duplicate=True),
          Input("clear-legs-btn", "n_clicks"), prevent_initial_call=True)
def clear_legs(n):
    return [] if n else no_update


@callback(Output("legs-store", "data", allow_duplicate=True),
          Input("preset-cc", "n_clicks"),
          State("symbol-store", "data"),
          State("rows-store", "data"), prevent_initial_call=True)
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


@callback(Output("legs-store", "data", allow_duplicate=True),
          Input("preset-cs", "n_clicks"),
          State("symbol-store", "data"),
          State("rows-store", "data"), prevent_initial_call=True)
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


@callback(Output("legs-store", "data", allow_duplicate=True),
          Input("preset-ic", "n_clicks"),
          State("symbol-store", "data"),
          State("rows-store", "data"), prevent_initial_call=True)
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


@callback(Output("legs-store", "data", allow_duplicate=True),
          Input("preset-st", "n_clicks"),
          State("symbol-store", "data"),
          State("rows-store", "data"), prevent_initial_call=True)
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


@callback(Output("legs-list", "children"),
          Input("legs-store", "data"),
          Input("theme-store", "data"),
          Input("lang-store", "data"))
def render_legs(legs, theme, lang):
    t = THEMES[theme]
    s = STRINGS[lang]
    if not legs:
        return html.Span(s["no_legs"], style={"fontSize": "12px", "color": t["muted"]})
    items = []
    for i, leg in enumerate(legs):
        color = PROFIT if leg["side"] > 0 else RED
        side_text = "LONG" if leg["side"] > 0 else "SHORT"
        if leg["type"] == "underlying":
            detail = f"{leg['instrument']} (spot)"
        else:
            detail = f"{leg['type'].upper()} K={leg['strike']} @ ${round(leg['premium'], 2)}"
        items.append(html.Div([
            html.Span(f"#{i+1} ", style={"color": t["muted"], "fontSize": "11px"}),
            html.Span(f"{side_text} ", style={"color": color, "fontWeight": "700", "fontSize": "12px"}),
            html.Span(detail, style={"color": t["text"], "fontSize": "12px"}),
        ], style={"padding": "3px 0", "borderBottom": f"1px solid {t['border']}"}))
    return items


@callback(Output("chart", "figure"),
          Input("legs-store", "data"),
          Input("chain-grid", "selectedRows"),
          State("symbol-store", "data"),
          State("theme-store", "data"),
          prevent_initial_call=False)
def update_chart(legs, selected, symbol, theme):
    symbol = symbol or "BTC"
    theme = theme or "dark"
    if symbol in CRYPTO_SYMBOLS:
        spot = get_crypto_spot(symbol)
    else:
        spot = get_stock_spot(symbol)
    if spot is None:
        spot = 100
    if legs:
        return make_multi_leg_chart(spot, legs, symbol, theme)
    if selected:
        row = selected[0]
        strike = row.get("strike", 0)
        premium = row.get("bid") or 0
        if strike:
            return make_preview_chart(spot, strike, premium, symbol, theme)
    t = THEMES[theme]
    fig = go.Figure()
    fig.update_layout(
        paper_bgcolor=t["chart_bg"], plot_bgcolor=t["chart_bg"],
        font=dict(color=t["text"]),
        annotations=[dict(text="Loading…", x=0.5, y=0.5, xref="paper", yref="paper",
                          showarrow=False, font=dict(color=t["muted"], size=14))],
    )
    return fig


@callback(Output("root", "style"),
          Output("header", "style"),
          Output("symbol-row", "style"),
          Output("expiry-row", "style"),
          Output("preset-row", "style"),
          Output("grid-panel", "style"),
          Output("grid-header", "style"),
          Output("manual-row", "style"),
          Output("legs-panel", "style"),
          Output("chart-panel", "style"),
          Output("chain-grid", "className"),
          Output("theme-toggle", "style"),
          Output("theme-toggle", "children"),
          Output("lang-toggle", "style"),
          Output("about-btn", "style"),
          Output("analysis-btn", "style"),
          Input("theme-store", "data"),
          prevent_initial_call=False)
def apply_theme(theme):
    t = THEMES[theme]
    root_style = {"minHeight": "100vh",
                  "fontFamily": "Inter, -apple-system, Segoe UI, sans-serif",
                  "background": t["bg"], "color": t["text"]}
    header_style = {"display": "flex", "alignItems": "center",
                    "padding": "16px 24px", "background": t["panel"],
                    "borderBottom": f"1px solid {t['border']}"}
    row_style = {"display": "flex", "alignItems": "center",
                 "padding": "12px 24px 0 24px", "flexWrap": "wrap",
                 "background": t["bg"], "color": t["text"]}
    expiry_style = {"display": "flex", "alignItems": "center",
                    "padding": "12px 24px", "flexWrap": "wrap",
                    "background": t["bg"], "color": t["text"]}
    preset_style = {"display": "flex", "alignItems": "center",
                    "padding": "0 24px 12px 24px", "flexWrap": "wrap",
                    "background": t["bg"], "color": t["text"]}
    panel_style = {"borderRadius": "8px", "overflow": "hidden",
                   "background": t["panel"], "border": f"1px solid {t['border']}",
                   "boxShadow": t["shadow"]}
    grid_header_style = {"padding": "12px 16px", "background": t["panel"],
                         "borderBottom": f"1px solid {t['border']}"}
    manual_row_style = {"padding": "0 16px 12px 16px",
                        "borderBottom": f"1px solid {t['border']}"}
    legs_panel_style = {"padding": "12px 16px", "minHeight": "100px",
                        "maxHeight": "180px", "overflowY": "auto",
                        "borderTop": f"1px solid {t['border']}"}
    button_style = {"fontSize": "18px", "padding": "8px 14px",
                    "borderRadius": "10px", "cursor": "pointer",
                    "border": f"1px solid {t['border']}",
                    "background": t["panel"], "color": t["text"]}
    btn_style = {"marginLeft": "12px", "background": t["btn_bg"], "color": t["text"],
                 "border": f"1px solid {t['border']}", "padding": "9px 14px",
                 "borderRadius": "8px", "fontSize": "12px", "fontWeight": "600",
                 "cursor": "pointer"}
    analysis_btn_style = {"marginLeft": "8px", "background": t["btn_bg"],
                          "color": t["text"], "border": f"1px solid {t['border']}",
                          "padding": "9px 14px", "borderRadius": "8px",
                          "fontSize": "12px", "fontWeight": "600", "cursor": "pointer"}
    grid_class = t["grid_theme"]
    icon = "☀️" if theme == "dark" else "🌙"
    return (root_style, header_style, row_style, expiry_style, preset_style,
            panel_style, grid_header_style, manual_row_style, legs_panel_style,
            panel_style, grid_class, button_style, icon, button_style, btn_style,
            analysis_btn_style)


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8051))
    app.run(debug=False, host="0.0.0.0", port=port)