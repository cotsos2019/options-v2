"""
Options Dashboard v2 — Stage 20
+ Crypto contract size = 0.1 BTC (Deribit minimum)
+ Stocks = 100 shares
+ Options-Lab-style analysis modal (Outcomes, Break-even vs full, Warnings, Execution)
+ Full bilingual EL/EN
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
import math
from datetime import datetime, timezone
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
        "presets_hint": "👉 Αυτόματες — διαλέγουν strikes με βάση το spot",
        "chain": "📋 Options Chain",
        "legs": "🎯 Στρατηγική (Legs)",
        "all": "ΟΛΑ", "calls": "CALLS", "puts": "PUTS",
        "long": "＋ LONG", "short": "－ SHORT",
        "manual_hint": "👉 Manual — χρησιμοποιεί τη γραμμή που διάλεξες",
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
        "analysis_title": "📊 Ανάλυση Στρατηγικής",
        "analysis_no_legs": "⚠️ Δεν έχεις legs. Κλίκαρε γραμμή + **+ LONG / + SHORT** ή διάλεξε preset.",
        "analysis_your_legs": "🎯 Τα legs σου",
        "analysis_chart": "📈 Διάγραμμα Κέρδους / Ζημιάς",
        "analysis_scenarios": "🎲 Σενάρια",
        "analysis_summary": "💰 Σύνοψη",
        "analysis_max_profit": "Μέγιστο κέρδος",
        "analysis_max_loss": "Μέγιστη ζημιά",
        "analysis_breakevens": "Break-even",
        "analysis_win_zone": "🟢 Κερδίζεις όταν",
        "analysis_lose_zone": "🔴 Χάνεις όταν",
        "analysis_net_cost": "Καθαρό κόστος",
        "analysis_scenario_case": "Αν η τιμή πάει…",
        "analysis_scenario_result": "Τότε…",
        "analysis_scenario_profit": "Κέρδος",
        "analysis_scenario_loss": "Ζημιά",
        "unlimited": "Απεριόριστο",
        "exec_title": "⚙️ Εντολές Εκτέλεσης",
        "exec_buy": "ΑΓΟΡΑ",
        "exec_sell": "ΠΩΛΗΣΗ",
        "exec_capital": "Απαιτούμενο Κεφάλαιο",
        "exec_contracts": "συμβόλαια",
        "warn_title": "⚠️ Προειδοποιήσεις",
        "warn_below": "Αν πέσει κάτω από",
        "warn_above": "Αν ανέβει πάνω από",
        "warn_less_usd": "θα έχεις λιγότερα USD",
        "warn_less_crypto": "θα έχεις λιγότερα BTC",
        "warn_less_stock": "θα έχεις λιγότερες μετοχές",
        "one_contract_crypto": "1 συμβόλαιο = 0.1 BTC/ETH",
        "one_contract_stock": "1 συμβόλαιο = 100 μετοχές",
        "greeks_title": "📐 Greeks",
        "greek_delta": "Delta", "greek_gamma": "Gamma",
        "greek_theta": "Theta", "greek_vega": "Vega",
        "greek_delta_desc": "Πόσο αλλάζει η τιμή του option αν το spot κινηθεί $1.",
        "greek_gamma_desc": "Πόσο αλλάζει το Delta αν το spot κινηθεί $1.",
        "greek_theta_desc": "Πόσο χάνει η αξία του option κάθε μέρα (time decay).",
        "greek_vega_desc": "Πόσο αλλάζει η τιμή αν το IV κινηθεί 1%.",
        "greeks_note": "Crypto & Stocks: Black-Scholes από το IV.",
        "outcomes_title": "📊 Αποτελέσματα στη Λήξη",
        "outcomes_above": "Αν {sym} ≥ ${strike}",
        "outcomes_below": "Αν {sym} < ${strike}",
        "outcomes_prob": "prob",
        "even_title": "📍 Σημεία Ισορροπίας",
        "even_vs_usd": "Ίσα με full USD",
        "even_vs_crypto": "Ίσα με full BTC",
        "even_vs_stock": "Ίσα με full shares",
        "min_position": "Ελάχιστη θέση",
        "vs_full_usd": "ίδιο με full USD",
        "vs_full_crypto": "ίδιο με full BTC",
        "vs_full_stock": "ίδιο με full shares",
    },
    "en": {
        "title": "📊 Options Dashboard",
        "subtitle": "Crypto + Stocks options dashboard",
        "symbol": "💰 Symbol:",
        "expiry": "📅 Expiry:",
        "presets": "⚡ Strategies (auto from spot):",
        "presets_hint": "👉 Automatic — pick strikes from spot",
        "chain": "📋 Options Chain",
        "legs": "🎯 Strategy Legs",
        "all": "ALL", "calls": "CALLS", "puts": "PUTS",
        "long": "＋ LONG", "short": "－ SHORT",
        "manual_hint": "👉 Manual — uses the row you picked",
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
        "analysis_title": "📊 Strategy Analysis",
        "analysis_no_legs": "⚠️ No legs. Click a row + **+ LONG / + SHORT** or pick a preset.",
        "analysis_your_legs": "🎯 Your legs",
        "analysis_chart": "📈 Profit / Loss Chart",
        "analysis_scenarios": "🎲 Scenarios",
        "analysis_summary": "💰 Summary",
        "analysis_max_profit": "Max profit",
        "analysis_max_loss": "Max loss",
        "analysis_breakevens": "Break-even",
        "analysis_win_zone": "🟢 You win when",
        "analysis_lose_zone": "🔴 You lose when",
        "analysis_net_cost": "Net cost",
        "analysis_scenario_case": "If price goes to…",
        "analysis_scenario_result": "Then…",
        "analysis_scenario_profit": "Profit",
        "analysis_scenario_loss": "Loss",
        "unlimited": "Unlimited",
        "exec_title": "⚙️ Execution Instructions",
        "exec_buy": "BUY",
        "exec_sell": "SELL",
        "exec_capital": "Capital Required",
        "exec_contracts": "contracts",
        "warn_title": "⚠️ Warnings",
        "warn_below": "If it falls below",
        "warn_above": "If it rises above",
        "warn_less_usd": "you'll have less USD",
        "warn_less_crypto": "you'll have less BTC",
        "warn_less_stock": "you'll have fewer shares",
        "one_contract_crypto": "1 contract = 0.1 BTC/ETH",
        "one_contract_stock": "1 contract = 100 shares",
        "greeks_title": "📐 Greeks",
        "greek_delta": "Delta", "greek_gamma": "Gamma",
        "greek_theta": "Theta", "greek_vega": "Vega",
        "greek_delta_desc": "How much the option price changes if spot moves $1.",
        "greek_gamma_desc": "How much Delta changes if spot moves $1.",
        "greek_theta_desc": "How much value the option loses each day (time decay).",
        "greek_vega_desc": "How much the price changes if IV moves 1%.",
        "greeks_note": "Crypto & Stocks: Black-Scholes from IV.",
        "outcomes_title": "📊 Outcomes at Expiration",
        "outcomes_above": "If {sym} ≥ ${strike}",
        "outcomes_below": "If {sym} < ${strike}",
        "outcomes_prob": "prob",
        "even_title": "📍 Break-even Points",
        "even_vs_usd": "Even vs full USD",
        "even_vs_crypto": "Even vs full BTC",
        "even_vs_stock": "Even vs full shares",
        "min_position": "Minimum position",
        "vs_full_usd": "even with full USD",
        "vs_full_crypto": "even with full BTC",
        "vs_full_stock": "even with full shares",
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
WARN = "#f39c12"
GREEK = "#9b59b6"

CRYPTO_SYMBOLS = {"BTC", "ETH"}
ALL_SYMBOLS = ["BTC", "ETH", "AAPL", "SPY", "TSLA", "NVDA", "MSFT", "QQQ"]

CRYPTO_CONTRACT = 0.1     # 1 option = 0.1 BTC/ETH
STOCK_CONTRACT = 100      # 1 option = 100 shares

_stock_session = curl_requests.Session(impersonate="chrome")
_stock_session.verify = False


def _norm_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _norm_pdf(x):
    return (1.0 / math.sqrt(2.0 * math.pi)) * math.exp(-0.5 * x * x)


def bs_greeks(S, K, T, r, sigma, opt_type):
    try:
        if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
            return {"delta": None, "gamma": None, "theta": None, "vega": None}
        d1 = (math.log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
        if opt_type == "call":
            delta = _norm_cdf(d1)
            theta = (-S * _norm_pdf(d1) * sigma / (2 * math.sqrt(T))
                     - r * K * math.exp(-r * T) * _norm_cdf(d2)) / 365.0
        else:
            delta = _norm_cdf(d1) - 1.0
            theta = (-S * _norm_pdf(d1) * sigma / (2 * math.sqrt(T))
                     + r * K * math.exp(-r * T) * _norm_cdf(-d2)) / 365.0
        gamma = _norm_pdf(d1) / (S * sigma * math.sqrt(T))
        vega = S * _norm_pdf(d1) * math.sqrt(T) / 100.0
        return {
            "delta": round(delta, 4),
            "gamma": round(gamma, 6),
            "theta": round(theta, 4),
            "vega": round(vega, 4),
        }
    except Exception:
        return {"delta": None, "gamma": None, "theta": None, "vega": None}


def bs_prob_itm(S, K, T, r, sigma, opt_type):
    try:
        if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
            return None
        d2 = (math.log(S / K) + (r - 0.5 * sigma * sigma) * T) / (sigma * math.sqrt(T))
        if opt_type == "call":
            return _norm_cdf(d2)
        else:
            return _norm_cdf(-d2)
    except Exception:
        return None


def _years_to_expiry(expiry_str):
    try:
        exp = datetime.strptime(expiry_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        seconds = (exp - now).total_seconds()
        return max(seconds / (365.0 * 24 * 3600), 0.0)
    except Exception:
        return 0.0


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

    T = _parse_deribit_expiry_to_years(expiry_label)

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

        if bid_usd is not None and ask_usd is not None:
            premium = (bid_usd + ask_usd) / 2
        else:
            premium = bid_usd or ask_usd or 0

        iv_pct = item.get("mark_iv")
        iv_dec = (iv_pct / 100.0) if iv_pct else None

        prob = None
        if iv_dec and spot and T > 0:
            prob = bs_prob_itm(spot, strike, T, 0.045, iv_dec, opt_type)

        greeks = {"delta": None, "gamma": None, "theta": None, "vega": None}
        if iv_dec and spot and T > 0:
            greeks = bs_greeks(spot, strike, T, 0.045, iv_dec, opt_type)

        # Capital = ask price * 0.1 BTC
        capital_long = ask_usd * CRYPTO_CONTRACT if ask_usd else None

        rows.append({
            "instrument": name,
            "type": opt_type,
            "strike": strike,
            "bid": bid_usd,
            "ask": ask_usd,
            "premium": round(premium, 2) if premium else None,
            "capital": round(capital_long, 2) if capital_long else None,
            "prob_itm": round(prob, 4) if prob is not None else None,
            "delta": greeks["delta"],
            "gamma": greeks["gamma"],
            "theta": greeks["theta"],
            "vega": greeks["vega"],
            "iv": iv_pct,
            "volume": item.get("volume"),
            "oi": item.get("open_interest"),
        })
    cache_set(key, rows, ttl=60)
    return rows


def _parse_deribit_expiry_to_years(label):
    try:
        day = int(label[:2])
        mon_str = label[2:5]
        year = int("20" + label[5:7])
        months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN",
                  "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
        month = months.index(mon_str) + 1
        exp = datetime(year, month, day, 8, 0, 0, tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        sec = (exp - now).total_seconds()
        return max(sec / (365.0 * 24 * 3600), 0.0)
    except Exception:
        return 0.0


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
    T = _years_to_expiry(expiry)
    r_rate = 0.045

    rows = []
    for _, row in chain.calls.iterrows():
        rows.append(_stock_row(row, symbol, expiry, "call", spot, T, r_rate))
    for _, row in chain.puts.iterrows():
        rows.append(_stock_row(row, symbol, expiry, "put", spot, T, r_rate))
    rows.sort(key=lambda x: abs(x["strike"] - spot))
    rows = rows[:max_strikes]
    rows.sort(key=lambda x: (x["strike"], 0 if x["type"] == "call" else 1))
    cache_set(key, rows, ttl=120)
    return rows


def _stock_row(r, symbol, expiry, opt_type, spot, T, r_rate):
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
        iv_dec = 0
        iv_pct = 0
    else:
        iv_dec = iv
        iv_pct = iv * 100

    premium = (bid + ask) / 2 if (bid or ask) else last
    capital = ask * STOCK_CONTRACT if ask > 0 else None

    prob = None
    if iv_dec > 0 and spot and T > 0:
        prob = bs_prob_itm(spot, strike, T, r_rate, iv_dec, opt_type)

    greeks = {"delta": None, "gamma": None, "theta": None, "vega": None}
    if iv_dec > 0 and spot and T > 0:
        greeks = bs_greeks(spot, strike, T, r_rate, iv_dec, opt_type)

    suffix = "C" if opt_type == "call" else "P"
    return {
        "instrument": f"{symbol}-{expiry}-{strike}-{suffix}",
        "type": opt_type,
        "strike": strike,
        "bid": bid,
        "ask": ask,
        "premium": round(premium, 2),
        "capital": round(capital, 2) if capital else None,
        "prob_itm": round(prob, 4) if prob is not None else None,
        "delta": greeks["delta"],
        "gamma": greeks["gamma"],
        "theta": greeks["theta"],
        "vega": greeks["vega"],
        "iv": iv_pct,
        "volume": int(volume),
        "oi": int(_clean(r.get("openInterest"))),
    }


# ============================================================
# ANALYSIS
# ============================================================
def analyze_strategy(spot, legs, symbol, lang, chain_rows=None):
    if not legs:
        return None
    s = STRINGS[lang]
    is_crypto = symbol in CRYPTO_SYMBOLS
    multiplier = CRYPTO_CONTRACT if is_crypto else STOCK_CONTRACT

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
                pnl += side * (p - spot) * multiplier
            elif leg["type"] == "call":
                pnl += side * (max(p - leg["strike"], 0) - prem) * multiplier
            elif leg["type"] == "put":
                pnl += side * (max(leg["strike"] - p, 0) - prem) * multiplier
        return pnl

    pnls = [payoff(p) for p in prices]

    net_cost = 0.0
    for leg in legs:
        if leg["type"] == "underlying":
            net_cost += leg["side"] * spot * multiplier
        else:
            net_cost += -1 * leg["side"] * leg["premium"] * multiplier

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

    test_prices = sorted(set([
        round(spot * 0.90, 2), round(spot * 0.95, 2), round(spot, 2),
        round(spot * 1.05, 2), round(spot * 1.10, 2), round(spot * 1.15, 2),
    ]))
    while len(test_prices) < 6:
        test_prices.append(round(test_prices[-1] * 1.05, 2))
    test_prices = test_prices[:6]

    scenarios = []
    for p in test_prices:
        pnl = payoff(p)
        scenarios.append({"price": p, "pnl": round(pnl, 2), "is_profit": pnl >= 0})

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
                             fill="tozeroy", fillcolor="rgba(46, 204, 113, 0.25)",
                             name=s["analysis_scenario_profit"]))
    fig.add_trace(go.Scatter(x=loss_x, y=loss_y, mode="lines",
                             line=dict(color=LOSS, width=3),
                             fill="tozeroy", fillcolor="rgba(231, 76, 60, 0.25)",
                             name=s["analysis_scenario_loss"]))
    fig.add_hline(y=0, line_dash="dash", line_color="#8b949e")
    fig.add_vline(x=spot, line_dash="dot", line_color=SPOT, line_width=2,
                  annotation_text=f"Spot ${spot:,.0f}", annotation_position="top",
                  annotation_font=dict(color=SPOT, size=11))
    for k in sorted(set(strikes)):
        fig.add_vline(x=k, line_dash="dot", line_color=STRIKE, line_width=1,
                      annotation_text=f"K={k:,.0f}", annotation_position="bottom",
                      annotation_font=dict(color=STRIKE, size=9))
    for be in breakevens:
        fig.add_vline(x=be, line_dash="dot", line_color=WARN, line_width=1,
                      annotation_text=f"BE ${be:,.0f}", annotation_position="top right",
                      annotation_font=dict(color=WARN, size=10))

    fig.update_layout(
        paper_bgcolor="#161b22", plot_bgcolor="#161b22",
        font=dict(color="#e6edf3", size=11),
        xaxis=dict(title=dict(text="Price at Expiry", font=dict(color="#e6edf3")),
                   tickfont=dict(color="#8b949e"), gridcolor="#30363d"),
        yaxis=dict(title=dict(text="P&L ($)", font=dict(color="#e6edf3")),
                   tickfont=dict(color="#8b949e"), gridcolor="#30363d"),
        margin=dict(l=60, r=30, t=30, b=50),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1, font=dict(color="#8b949e", size=10)),
        height=320,
    )

    # Execution instructions (with 0.1 BTC or 100 shares)
    exec_steps = []
    capital_usd = 0.0
    capital_crypto = 0.0
    for leg in legs:
        if leg["type"] == "underlying":
            qty = multiplier
            cost = spot * qty * leg["side"]
            action = "BUY" if leg["side"] > 0 else "SELL"
            if is_crypto:
                desc = f"{qty} {leg['instrument']} @ ${spot:,.2f}"
            else:
                desc = f"{int(qty)} shares {leg['instrument']} @ ${spot:,.2f}"
            exec_steps.append({"action": action, "desc": desc, "cost": cost})
            if leg["side"] > 0:
                capital_usd += abs(cost)
                if is_crypto:
                    capital_crypto += qty
        else:
            qty = multiplier
            cost = leg["premium"] * qty * leg["side"]
            action = "BUY" if leg["side"] > 0 else "SELL"
            if is_crypto:
                opt_desc = f"1 {leg['type'].upper()} K=${leg['strike']:,.0f} (0.1 BTC) @ ${leg['premium']:,.2f}"
            else:
                opt_desc = f"1 {leg['type'].upper()} K=${leg['strike']:,.0f} (100 shares) @ ${leg['premium']:,.2f}"
            exec_steps.append({"action": action, "desc": opt_desc, "cost": cost})
            if leg["side"] > 0:
                capital_usd += abs(cost)

    # Outcomes at expiration (Options-Lab style)
    outcomes = []
    if len(legs) == 2:
        has_underlying = any(l["type"] == "underlying" and l["side"] > 0 for l in legs)
        has_short_call = any(l["type"] == "call" and l["side"] < 0 for l in legs)
        if has_underlying and has_short_call:
            short_call = next(l for l in legs if l["type"] == "call" and l["side"] < 0)
            k = short_call["strike"]
            prem_btc = short_call["premium"] / spot if spot else 0  # convert USD premium to BTC

            # Scenario 1: price >= strike (call exercised)
            payoff_above = payoff(k * 1.01)  # slightly above strike
            pnl_pct_above = (payoff_above / capital_usd * 100) if capital_usd else 0
            prob_above = None
            if chain_rows:
                for r in chain_rows:
                    if r["instrument"] == short_call["instrument"]:
                        prob_above = r.get("prob_itm")
                        break
            if prob_above is None:
                prob_above = 0.5

            outcomes.append({
                "label": s["outcomes_above"].format(sym=symbol, strike=f"{k:,.0f}"),
                "pnl_usd": payoff_above,
                "pnl_pct": pnl_pct_above,
                "prob": prob_above,
                "extra": f"+{prem_btc:.4f} BTC",
                "color": PROFIT,
            })

            # Scenario 2: price < strike (call expires worthless)
            payoff_below = prem_btc * spot * (CRYPTO_CONTRACT if is_crypto else STOCK_CONTRACT)
            pnl_pct_below = (payoff_below / capital_usd * 100) if capital_usd else 0
            outcomes.append({
                "label": s["outcomes_below"].format(sym=symbol, strike=f"{k:,.0f}"),
                "pnl_usd": payoff_below,
                "pnl_pct": pnl_pct_below,
                "prob": 1 - prob_above,
                "extra": f"+{prem_btc:.4f} BTC",
                "color": PROFIT,
            })

    # Break-even vs full USD/BTC
    even_vs = {}
    if len(legs) == 2:
        has_underlying = any(l["type"] == "underlying" and l["side"] > 0 for l in legs)
        has_short_call = any(l["type"] == "call" and l["side"] < 0 for l in legs)
        if has_underlying and has_short_call:
            short_call = next(l for l in legs if l["type"] == "call" and l["side"] < 0)
            k = short_call["strike"]
            p = short_call["premium"]  # USD premium per unit
            # Even vs USD: strike - premium
            even_vs["usd"] = round(k - p, 2)
            # Even vs BTC: strike + premium
            even_vs["crypto"] = round(k + p, 2)

    # Warnings
    warnings = []
    if even_vs:
        k = even_vs.get("usd")
        up = even_vs.get("crypto")
        if k:
            warnings.append({
                "text": f"{s['warn_below']} ${k:,.2f} ({(k/spot-1)*100:+.1f}%), {s['warn_less_usd']}",
            })
        if up:
            warn_less = s["warn_less_crypto"] if is_crypto else s["warn_less_stock"]
            warnings.append({
                "text": f"{s['warn_above']} ${up:,.2f} ({(up/spot-1)*100:+.1f}%), {warn_less}",
            })

    return {
        "chart": fig,
        "scenarios": scenarios,
        "net_cost": round(net_cost, 2),
        "max_profit": max_profit,
        "max_loss": max_loss,
        "breakevens": breakevens,
        "win_ranges": win_ranges,
        "spot": spot,
        "legs": legs,
        "exec_steps": exec_steps,
        "capital_usd": round(capital_usd, 2),
        "capital_crypto": round(capital_crypto, 6),
        "outcomes": outcomes,
        "even_vs": even_vs,
        "warnings": warnings,
        "multiplier": multiplier,
        "is_crypto": is_crypto,
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
    analysis = analyze_strategy(spot, legs, symbol, "en")
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
                   font=dict(color=t["text"], size=14), x=0.02),
        xaxis=dict(title=dict(text=f"{symbol} Price at Expiry", font=dict(color=t["text"])),
                   tickfont=dict(color=t["muted"]), gridcolor=t["border"], zerolinecolor=t["border"]),
        yaxis=dict(title=dict(text="Profit / Loss ($)", font=dict(color=t["text"])),
                   tickfont=dict(color=t["muted"]), gridcolor=t["border"], zerolinecolor=t["border"]),
        paper_bgcolor=t["chart_bg"], plot_bgcolor=t["chart_bg"],
        font=dict(color=t["text"]),
        hovermode="x unified", margin=dict(l=50, r=20, t=60, b=40), showlegend=False,
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
                --ag-font-size: 12px;
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
                --ag-font-size: 12px;
            }

            .ds-hint {
                font-size: 11px;
                color: #8b949e;
                font-style: italic;
                margin-left: 8px;
                padding: 2px 8px;
                border-left: 2px solid #30363d;
            }

            .exec-card {
                background: rgba(31, 111, 235, 0.08);
                border-left: 3px solid #1f6feb;
                border-radius: 8px;
                padding: 12px 16px;
                margin-bottom: 12px;
            }
            .exec-action {
                display: inline-block;
                font-weight: 700;
                font-size: 11px;
                padding: 3px 8px;
                border-radius: 4px;
                margin-right: 8px;
                letter-spacing: 0.5px;
            }
            .exec-buy { background: rgba(46, 204, 113, 0.2); color: #2ecc71; }
            .exec-sell { background: rgba(231, 76, 60, 0.2); color: #e74c3c; }

            .warn-card {
                background: rgba(243, 156, 18, 0.1);
                border-left: 3px solid #f39c12;
                border-radius: 8px;
                padding: 10px 14px;
                margin-bottom: 8px;
                font-size: 13px;
            }

            .greek-card {
                background: rgba(155, 89, 182, 0.08);
                border-left: 3px solid #9b59b6;
                border-radius: 8px;
                padding: 14px 18px;
                margin-bottom: 12px;
            }
            .greek-grid {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 12px;
            }
            .greek-cell {
                background: rgba(255,255,255,0.03);
                border-radius: 6px;
                padding: 10px;
                text-align: center;
            }
            .greek-label {
                font-size: 10px;
                color: #8b949e;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 4px;
            }
            .greek-value {
                font-size: 16px;
                font-weight: 700;
                color: #9b59b6;
            }
            .greek-desc {
                font-size: 10px;
                color: #8b949e;
                margin-top: 4px;
                font-style: italic;
            }

            .outcome-row {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 10px 14px;
                border-bottom: 1px solid #30363d;
                font-size: 13px;
            }
            .outcome-row:last-child { border-bottom: none; }
            .outcome-label { flex: 2; }
            .outcome-pnl { flex: 1; text-align: right; font-weight: 700; }
            .outcome-prob { flex: 1; text-align: right; color: #8b949e; font-size: 12px; }

            @media (max-width: 1200px) {
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
                    {"field": "instrument", "headerName": "Instrument", "flex": 2, "minWidth": 180},
                    {"field": "type", "headerName": "Type", "flex": 1, "minWidth": 55,
                     "cellStyle": {"function": "params.value === 'call' ? {color: '#2ecc71', fontWeight: 600} : {color: '#e74c3c', fontWeight: 600}"}},
                    {"field": "strike", "headerName": "Strike", "flex": 1, "minWidth": 75,
                     "valueFormatter": {"function": "params.value ? '$' + params.value.toLocaleString() : ''"}},
                    {"field": "bid", "headerName": "Bid", "flex": 1, "minWidth": 70,
                     "valueFormatter": {"function": "params.value != null ? '$' + Number(params.value).toFixed(2) : ''"}},
                    {"field": "ask", "headerName": "Ask", "flex": 1, "minWidth": 70,
                     "valueFormatter": {"function": "params.value != null ? '$' + Number(params.value).toFixed(2) : ''"}},
                    {"field": "premium", "headerName": "Prem", "flex": 1, "minWidth": 75,
                     "valueFormatter": {"function": "params.value != null ? '$' + Number(params.value).toFixed(2) : ''"}},
                    {"field": "capital", "headerName": "Capital", "flex": 1, "minWidth": 85,
                     "valueFormatter": {"function": "params.value != null ? '$' + Number(params.value).toLocaleString() : ''"}},
                    {"field": "delta", "headerName": "Δ", "flex": 1, "minWidth": 55,
                     "valueFormatter": {"function": "params.value != null ? Number(params.value).toFixed(3) : '—'"},
                     "cellStyle": {"function": "params.value == null ? {} : {color: '#9b59b6', fontWeight: 600}"}},
                    {"field": "gamma", "headerName": "Γ", "flex": 1, "minWidth": 60,
                     "valueFormatter": {"function": "params.value != null ? Number(params.value).toFixed(5) : '—'"},
                     "cellStyle": {"function": "params.value == null ? {} : {color: '#9b59b6', fontWeight: 600}"}},
                    {"field": "theta", "headerName": "Θ", "flex": 1, "minWidth": 60,
                     "valueFormatter": {"function": "params.value != null ? Number(params.value).toFixed(3) : '—'"},
                     "cellStyle": {"function": "params.value == null ? {} : {color: '#9b59b6', fontWeight: 600}"}},
                    {"field": "vega", "headerName": "V", "flex": 1, "minWidth": 55,
                     "valueFormatter": {"function": "params.value != null ? Number(params.value).toFixed(2) : '—'"},
                     "cellStyle": {"function": "params.value == null ? {} : {color: '#9b59b6', fontWeight: 600}"}},
                    {"field": "prob_itm", "headerName": "Prob", "flex": 1, "minWidth": 65,
                     "valueFormatter": {"function": "params.value != null ? (Number(params.value) * 100).toFixed(1) + '%' : ''"},
                     "cellStyle": {"function": "params.value == null ? {} : (params.value >= 0.5 ? {color: '#2ecc71', fontWeight: 600} : {color: '#e74c3c', fontWeight: 600})"}},
                    {"field": "iv", "headerName": "IV", "flex": 1, "minWidth": 55,
                     "valueFormatter": {"function": "params.value ? Number(params.value).toFixed(1) + '%' : ''"}},
                    {"field": "volume", "headerName": "Vol", "flex": 1, "minWidth": 50,
                     "valueFormatter": {"function": "params.value != null ? Number(params.value).toLocaleString() : ''"}},
                    {"field": "oi", "headerName": "OI", "flex": 1, "minWidth": 50,
                     "valueFormatter": {"function": "params.value != null ? Number(params.value).toLocaleString() : ''"}},
                ],
                rowData=[],
                style={"height": "calc(100vh - 460px)", "minHeight": "320px"},
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
                         children=html.Span("No legs yet",
                                            style={"fontSize": "12px"})),
            ], id="legs-panel", style={"padding": "12px 16px", "minHeight": "100px",
                                        "maxHeight": "180px", "overflowY": "auto"}),
        ], id="grid-panel", style={"borderRadius": "8px", "overflow": "hidden"}),

        html.Div([
            dcc.Graph(id="chart", style={"height": "calc(100vh - 260px)", "minHeight": "400px"},
                      config={"displayModeBar": False}),
        ], id="chart-panel", style={"borderRadius": "8px", "overflow": "hidden"}),
    ], id="main-grid", style={
        "display": "grid",
        "gridTemplateColumns": "1.9fr 1.1fr",
        "gap": "16px",
        "padding": "16px 24px",
    }),

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
        s["presets_hint"], s["chain"], s["legs"], s["long"], s["short"],
        s["manual_hint"], s["underlying"], s["clear"],
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
Αγοράζεις **0.1 BTC** (ή 100 shares), πουλάς OTM call.

### ↗️ Call Spread
Long call + short πιο ψηλό call.

### 🦅 Iron Condor
4 legs. Κερδίζεις αν η τιμή μείνει κοντά στο spot.

### ⚖️ Straddle
Long call + long put στο ίδιο strike.

### 📐 Greeks
- **Δ Delta** — Πόσο αλλάζει η τιμή αν το spot κινηθεί $1
- **Γ Gamma** — Πόσο αλλάζει το Delta αν το spot κινηθεί $1
- **Θ Theta** — Πόσο χάνει η αξία κάθε μέρα
- **V Vega** — Πόσο αλλάζει η τιμή αν το IV κινηθεί 1%

### 📏 Contract sizes
- **Crypto:** 1 συμβόλαιο = **0.1 BTC**
- **Stocks:** 1 συμβόλαιο = **100 shares**

---
💡 Πρόσθεσε legs και πάτα **📊 Ανάλυση Στρατηγικής**.
"""
    else:
        body = """
### 🛡️ Covered Call
Buy **0.1 BTC** (or 100 shares), sell OTM call.

### ↗️ Call Spread
Long call + short higher call.

### 🦅 Iron Condor
4 legs. Win if price stays near spot.

### ⚖️ Straddle
Long call + long put at same strike.

### 📐 Greeks
- **Δ Delta** — How much price changes if spot moves $1
- **Γ Gamma** — How much Delta changes if spot moves $1
- **Θ Theta** — How much value is lost each day
- **V Vega** — How much price changes if IV moves 1%

### 📏 Contract sizes
- **Crypto:** 1 contract = **0.1 BTC**
- **Stocks:** 1 contract = **100 shares**

---
💡 Add legs and press **📊 Strategy Analysis**.
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
    State("chain-grid", "rowData"),
)
def render_analysis_modal(is_open, legs, theme, lang, symbol, chain_rows):
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
                     "maxWidth": "950px", "width": "95%", "maxHeight": "90vh",
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

    analysis = analyze_strategy(spot, legs, symbol, lang, chain_rows)
    if not analysis:
        return (modal_style, content_style, title_style,
                html.Div("Error", style={"padding": "20px"}))

    body = []

    # ===== Outcomes at Expiration (Options Lab style) =====
    if analysis["outcomes"]:
        body.append(html.H3(s["outcomes_title"],
                            style={"fontSize": "15px", "marginTop": "0"}))
        outcome_rows = []
        for o in analysis["outcomes"]:
            pnl_color = PROFIT if o["pnl_usd"] >= 0 else LOSS
            outcome_rows.append(html.Div([
                html.Span(o["label"], className="outcome-label",
                          style={"fontWeight": "600", "color": t["text"]}),
                html.Span(f"${o['pnl_usd']:+,.2f} ({o['pnl_pct']:+.2f}%)",
                          className="outcome-pnl",
                          style={"color": pnl_color}),
                html.Span(f"({o['prob']*100:.0f}% {s['outcomes_prob']})",
                          className="outcome-prob"),
            ], className="outcome-row"))
        body.append(html.Div(outcome_rows, style={
            "background": t["panel_alt"], "borderRadius": "8px",
            "overflow": "hidden", "marginBottom": "16px"}))

    # ===== Break-even vs full =====
    if analysis["even_vs"]:
        body.append(html.H3(s["even_title"], style={"fontSize": "15px"}))
        even_rows = []
        if "usd" in analysis["even_vs"]:
            v = analysis["even_vs"]["usd"]
            label = s["even_vs_usd"]
            pct = (v / spot - 1) * 100
            even_rows.append(html.Div([
                html.Span(f"{label}: ", style={"color": t["muted"]}),
                html.Span(f"${v:,.2f}", style={"fontWeight": "700", "color": WARN}),
                html.Span(f" ({pct:+.1f}%)",
                          style={"color": t["muted"], "fontSize": "12px", "marginLeft": "6px"}),
            ], style={"padding": "6px 0"}))
        if "crypto" in analysis["even_vs"]:
            v = analysis["even_vs"]["crypto"]
            label = s["even_vs_crypto"] if analysis["is_crypto"] else s["even_vs_stock"]
            pct = (v / spot - 1) * 100
            even_rows.append(html.Div([
                html.Span(f"{label}: ", style={"color": t["muted"]}),
                html.Span(f"${v:,.2f}", style={"fontWeight": "700", "color": WARN}),
                html.Span(f" ({pct:+.1f}%)",
                          style={"color": t["muted"], "fontSize": "12px", "marginLeft": "6px"}),
            ], style={"padding": "6px 0"}))

        # Min position
        min_pos_label = s["min_position"]
        capital_usd = analysis["capital_usd"]
        capital_crypto = analysis["capital_crypto"]
        if analysis["is_crypto"] and capital_crypto > 0:
            even_rows.append(html.Div([
                html.Span(f"{min_pos_label}: ", style={"color": t["muted"]}),
                html.Span(f"${capital_usd:,.2f}", style={"fontWeight": "700", "color": ACCENT}),
                html.Span(f" ({capital_crypto:.3f} BTC)",
                          style={"color": t["muted"], "fontSize": "12px", "marginLeft": "6px"}),
            ], style={"padding": "6px 0"}))

        body.append(html.Div(even_rows, style={
            "background": t["panel_alt"], "padding": "12px 16px",
            "borderRadius": "8px", "marginBottom": "16px"}))

    # ===== Warnings =====
    if analysis["warnings"]:
        for w in analysis["warnings"]:
            body.append(html.Div(w["text"], className="warn-card"))

    # ===== Legs =====
    body.append(html.H3(s["analysis_your_legs"], style={"fontSize": "15px"}))
    leg_items = []
    for i, leg in enumerate(legs):
        side_color = PROFIT if leg["side"] > 0 else RED
        side_text = "LONG" if leg["side"] > 0 else "SHORT"
        if leg["type"] == "underlying":
            detail = f"{leg['instrument']} @ ${spot:,.2f}"
        else:
            detail = f"{leg['type'].upper()} K=${leg['strike']:,.0f} @ ${leg['premium']:,.2f}"
        leg_items.append(html.Div([
            html.Span(f"#{i+1} ", style={"color": t["muted"], "fontSize": "11px"}),
            html.Span(f"{side_text} ", style={"color": side_color, "fontWeight": "700", "fontSize": "13px"}),
            html.Span(detail, style={"color": t["text"], "fontSize": "13px"}),
        ], style={"padding": "4px 0", "borderBottom": f"1px solid {t['border']}"}))
    body.append(html.Div(leg_items, style={"marginBottom": "16px"}))

    # ===== Greeks =====
    greeks_lookup = {}
    if chain_rows:
        for r in chain_rows:
            greeks_lookup[r.get("instrument")] = {
                "delta": r.get("delta"),
                "gamma": r.get("gamma"),
                "theta": r.get("theta"),
                "vega": r.get("vega"),
            }

    greek_rows = []
    for leg in legs:
        if leg["type"] == "underlying":
            continue
        g = greeks_lookup.get(leg["instrument"], {})
        if g.get("delta") is None:
            continue
        weight = leg["side"] * analysis["multiplier"]
        greek_rows.append({
            "delta": (g.get("delta") or 0) * weight,
            "gamma": (g.get("gamma") or 0) * weight,
            "theta": (g.get("theta") or 0) * weight,
            "vega": (g.get("vega") or 0) * weight,
        })

    if greek_rows:
        td = sum(r["delta"] for r in greek_rows)
        tg = sum(r["gamma"] for r in greek_rows)
        tt = sum(r["theta"] for r in greek_rows)
        tv = sum(r["vega"] for r in greek_rows)
        body.append(html.H3(s["greeks_title"], style={"fontSize": "15px"}))
        greek_card = html.Div([
            html.Div([
                html.Div([
                    html.Div(s["greek_delta"], className="greek-label"),
                    html.Div(f"{td:,.3f}", className="greek-value"),
                    html.Div(s["greek_delta_desc"], className="greek-desc"),
                ], className="greek-cell"),
                html.Div([
                    html.Div(s["greek_gamma"], className="greek-label"),
                    html.Div(f"{tg:,.5f}", className="greek-value"),
                    html.Div(s["greek_gamma_desc"], className="greek-desc"),
                ], className="greek-cell"),
                html.Div([
                    html.Div(s["greek_theta"], className="greek-label"),
                    html.Div(f"{tt:,.3f}", className="greek-value"),
                    html.Div(s["greek_theta_desc"], className="greek-desc"),
                ], className="greek-cell"),
                html.Div([
                    html.Div(s["greek_vega"], className="greek-label"),
                    html.Div(f"{tv:,.2f}", className="greek-value"),
                    html.Div(s["greek_vega_desc"], className="greek-desc"),
                ], className="greek-cell"),
            ], className="greek-grid"),
            html.Div(s["greeks_note"],
                     style={"fontSize": "11px", "color": t["muted"],
                            "fontStyle": "italic", "marginTop": "10px"}),
        ], className="greek-card")
        body.append(greek_card)

    # ===== Execution Instructions =====
    body.append(html.H3(s["exec_title"], style={"fontSize": "15px"}))
    exec_rows = []
    for step in analysis["exec_steps"]:
        cls = "exec-buy" if step["action"] == "BUY" else "exec-sell"
        exec_rows.append(html.Div([
            html.Span(step["action"], className=f"exec-action {cls}"),
            html.Span(step["desc"], style={"color": t["text"], "fontSize": "13px"}),
            html.Span(f"  (${step['cost']:+,.2f})",
                      style={"color": PROFIT if step["cost"] < 0 else LOSS,
                             "fontWeight": "600", "marginLeft": "6px"}),
        ], style={"marginBottom": "6px"}))

    capital_usd = analysis["capital_usd"]
    capital_crypto = analysis["capital_crypto"]
    capital_text = f"${capital_usd:,.2f}"
    if analysis["is_crypto"] and capital_crypto > 0:
        capital_text += f" ({capital_crypto:.3f} BTC)"

    exec_card = html.Div([
        html.Div(exec_rows),
        html.Div([
            html.Span(s["exec_capital"] + ": ",
                      style={"fontWeight": "600", "fontSize": "13px"}),
            html.Span(capital_text,
                      style={"color": ACCENT, "fontWeight": "700", "fontSize": "15px"}),
        ], style={"marginTop": "12px", "paddingTop": "10px",
                  "borderTop": f"1px dashed {t['border']}"}),
        html.Div(s["one_contract_crypto" if analysis["is_crypto"] else "one_contract_stock"],
                 style={"fontSize": "11px", "color": t["muted"],
                        "fontStyle": "italic", "marginTop": "4px"}),
    ], className="exec-card")
    body.append(exec_card)

    # ===== Summary =====
    body.append(html.H3(s["analysis_summary"], style={"fontSize": "15px"}))
    net_cost = analysis["net_cost"]
    cost_color = RED if net_cost > 0 else PROFIT
    cost_label = f"${net_cost:,.2f}" if abs(net_cost) >= 0.01 else "$0"

    summary_rows = [
        html.Div([html.Span(s["analysis_net_cost"] + ": ", style={"fontWeight": "600"}),
                  html.Span(cost_label, style={"color": cost_color, "fontWeight": "700"})],
                 style={"marginBottom": "6px"}),
        html.Div([html.Span(s["analysis_max_profit"] + ": ", style={"fontWeight": "600"}),
                  html.Span(f"${analysis['max_profit']:,.2f}",
                            style={"color": PROFIT, "fontWeight": "700"})],
                 style={"marginBottom": "6px"}),
        html.Div([html.Span(s["analysis_max_loss"] + ": ", style={"fontWeight": "600"}),
                  html.Span(f"${analysis['max_loss']:,.2f}",
                            style={"color": LOSS, "fontWeight": "700"})],
                 style={"marginBottom": "6px"}),
    ]

    win_ranges = analysis["win_ranges"]
    if win_ranges:
        win_text = " or ".join([f"${a:,.0f} – ${b:,.0f}" for a, b in win_ranges])
        summary_rows.append(html.Div([
            html.Span(s["analysis_win_zone"] + ": ", style={"fontWeight": "600"}),
            html.Span(win_text, style={"color": PROFIT, "fontWeight": "700"}),
        ], style={"marginBottom": "6px"}))

    body.append(html.Div(summary_rows, style={
        "background": t["panel_alt"], "padding": "12px 16px",
        "borderRadius": "8px", "marginBottom": "16px"}))

    # ===== Chart =====
    body.append(html.H3(s["analysis_chart"], style={"fontSize": "15px"}))
    body.append(dcc.Graph(figure=analysis["chart"],
                          config={"displayModeBar": False},
                          style={"marginBottom": "16px", "height": "320px"}))

    # ===== Scenarios =====
    body.append(html.H3(s["analysis_scenarios"], style={"fontSize": "15px"}))
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
    body.append(html.Div(scenario_rows, style={
        "background": t["panel_alt"], "borderRadius": "8px",
        "overflow": "hidden", "marginBottom": "12px"}))

    return modal_style, content_style, title_style, body


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
          Output("main-grid", "style"),
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
    main_grid_style = {
        "display": "grid",
        "gridTemplateColumns": "1.9fr 1.1fr",
        "gap": "16px",
        "padding": "16px 24px",
    }
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
            panel_style, main_grid_style, grid_class, button_style, icon,
            button_style, btn_style, analysis_btn_style)


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8051))
    app.run(debug=False, host="0.0.0.0", port=port)