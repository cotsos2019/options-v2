"""
Options Dashboard v2 — Stage 27
+ Professional UI
+ Educational Analyze Modal
+ Save / Load Strategies
+ Fixed AG Grid (no more XSS warnings)
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
import db as strategies_db


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


DERIBIT = "https://www.deribit.com/api/v2"


STRINGS = {
    "el": {
        "title": "Options Dashboard",
        "subtitle": "Crypto & stocks options analytics",
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
        "iv_btn": "📈 IV Chart",
        "iv_chart_title": "📈 IV per Strike (Volatility Smile)",
        "guide_title": "📖 Οδηγός Στρατηγικών",
        "analysis_title": "📊 Ανάλυση Στρατηγικής",
        "iv_title": "📈 Volatility Smile",
        "analysis_no_legs": "⚠️ Δεν έχεις legs. Κλίκαρε γραμμή + **+ LONG / + SHORT** ή διάλεξε preset.",
        "analysis_your_legs": "🎯 Τα legs σου",
        "analysis_chart": "📈 Διάγραμμα Κέρδους / Ζημιάς",
        "analysis_scenarios": "🎲 Όλα τα Σενάρια",
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
        "greek_delta_desc": "Πόσο αλλάζει η τιμή αν το spot κινηθεί $1.",
        "greek_gamma_desc": "Πόσο αλλάζει το Delta αν το spot κινηθεί $1.",
        "greek_theta_desc": "Πόσο χάνει η αξία κάθε μέρα (time decay).",
        "greek_vega_desc": "Πόσο αλλάζει η τιμή αν το IV κινηθεί 1%.",
        "greeks_note": "Crypto & Stocks: Black-Scholes από το IV.",
        "outcomes_title": "📊 Αποτελέσματα στη Λήξη",
        "outcomes_prob": "prob",
        "even_title": "📍 Σημεία Ισορροπίας",
        "even_vs_usd": "Ίσα με full USD",
        "even_vs_crypto": "Ίσα με full BTC",
        "even_vs_stock": "Ίσα με full shares",
        "min_position": "Ελάχιστη θέση",
        "outcome_above": "Αν {sym} ≥ ${strike}",
        "outcome_below": "Αν {sym} < ${strike}",
        "outcome_between": "Αν ${lo} ≤ {sym} < ${hi}",
        "strike_modal_title": "🔍 Ανάλυση Strike",
        "analytics_table": "📊 Στοιχεία Options",
        "call_chart_title": "📈 Payoff CALL (Long)",
        "put_chart_title": "📉 Payoff PUT (Long)",
        "add_call_long": "🟢 ΑΓΟΡΑ CALL",
        "add_call_short": "🔴 ΠΟΥΛΑ CALL",
        "add_put_long": "🟢 ΑΓΟΡΑ PUT",
        "add_put_short": "🔴 ΠΟΥΛΑ PUT",
        "field": "Πεδίο",
        "call_label": "🔵 CALL",
        "put_label": "🔴 PUT",
        "strike_label": "Strike",
        "premium_label": "Premium",
        "capital_label": "Κεφάλαιο",
        "prob_itm_label": "Prob ITM",
        "break_even_label": "Break-even",
        "iv_calls": "Calls IV",
        "iv_puts": "Puts IV",
        "iv_spot": "Spot",
        "iv_strike": "Strike",
        "iv_iv": "IV (%)",
        "iv_no_data": "⚠️ Δεν υπάρχουν δεδομένα IV για αυτό το expiry.",
        "iv_hint": "Το Volatility Smile δείχνει πώς αλλάζει το IV ανά strike. Χαμηλό κοντά στο spot, υψηλό στα άκρα (wings).",
        # Stage 24: Educational Strike Modal
        "sm_what_is": "📖 Τι είναι αυτό το option;",
        "sm_what_is_call": "Ένα CALL option με strike **${strike}** σου δίνει το **δικαίωμα** (όχι υποχρέωση) να **ΑΓΟΡΑΣΕΙΣ** {sym} στα **${strike}** μέχρι τη λήξη. Κερδίζεις όταν το {sym} ανέβει πάνω από **${breakeven}**.",
        "sm_what_is_put": "Ένα PUT option με strike **${strike}** σου δίνει το **δικαίωμα** (όχι υποχρέωση) να **ΠΟΥΛΗΣΕΙΣ** {sym} στα **${strike}** μέχρι τη λήξη. Κερδίζεις όταν το {sym} πέσει κάτω από **${breakeven}**.",
        "sm_current_status": "📍 Τρέχουσα κατάσταση",
        "sm_spot_now": "Spot τώρα",
        "sm_moneyness": "Κατάσταση",
        "sm_moneyness_itm": "🟢 ITM (In The Money) — έχει εσωτερική αξία",
        "sm_moneyness_atm": "🟡 ATM (At The Money) — στο strike",
        "sm_moneyness_otm": "🔴 OTM (Out of The Money) — χωρίς εσωτερική αξία",
        "sm_moneyness_itm_short": "ITM",
        "sm_moneyness_atm_short": "ATM",
        "sm_moneyness_otm_short": "OTM",
        "sm_intrinsic": "Εσωτερική αξία",
        "sm_time_value": "Χρονική αξία",
        "sm_breakeven_short": "Break-even",
        "sm_breakeven_explain": "Η τιμή όπου δεν κερδίζεις ούτε χάνεις",
        "sm_table_title": "📊 Πίνακας δεδομένων",
        "sm_tooltip_strike": "Η τιμή στην οποία μπορείς να αγοράσεις/πουλήσεις το υποκείμενο",
        "sm_tooltip_bid": "Η τιμή που κάποιος είναι διατεθειμένος να ΑΓΟΡΑΣΕΙ το option",
        "sm_tooltip_ask": "Η τιμή που κάποιος είναι διατεθειμένος να ΠΟΥΛΗΣΕΙ το option",
        "sm_tooltip_premium": "Μέση τιμή (Bid + Ask) / 2 — αυτό πληρώνεις συνήθως",
        "sm_tooltip_iv": "Implied Volatility — πόσο volatile αναμένει η αγορά ότι θα είναι το {sym}",
        "sm_tooltip_delta": "Πόσο αλλάζει η τιμή του option αν το {sym} κινηθεί $1",
        "sm_tooltip_prob": "Πιθανότητα (Black-Scholes) το option να λήξει ITM",
        "sm_tooltip_capital": "Πόσα χρήματα χρειάζεσαι για 1 contract ({size})",
        "sm_interp_title": "💡 Τι σημαίνει για μένα;",
        "sm_interp_cheap": "Το premium είναι **χαμηλό** (${prem}). Φθηνό αλλά με μικρή πιθανότητα κέρδους ({prob}%).",
        "sm_interp_expensive": "Το premium είναι **υψηλό** (${prem}). Ακριβό αλλά με μεγάλη πιθανότητα κέρδους ({prob}%).",
        "sm_interp_mid": "Το premium είναι **μέτριο** (${prem}) με πιθανότητα κέρδους {prob}%.",
        "sm_interp_bullish": "Αν πιστεύεις ότι το {sym} θα **ΑΝΕΒΕΙ** → σκέψου **ΑΓΟΡΑ CALL**.",
        "sm_interp_bearish": "Αν πιστεύεις ότι το {sym} θα **ΠΕΣΕΙ** → σκέψου **ΑΓΟΡΑ PUT**.",
        "sm_interp_neutral": "Αν πιστεύεις ότι θα μείνει **σταθερό** → σκέψου **ΠΟΥΛΗΣΗ** option (short).",
        "sm_example_title": "🎯 Παράδειγμα (ΑΓΟΡΑ CALL)",
        "sm_example_up": "Αν το {sym} πάει **${price}** στη λήξη:",
        "sm_example_down": "Αν το {sym} μείνει **${price}** στη λήξη:",
        "sm_example_payoff": "Payoff",
        "sm_example_cost": "Κόστος",
        "sm_example_result": "Αποτέλεσμα",
        "sm_example_win": "ΚΕΡΔΟΣ",
        "sm_example_lose": "ΖΗΜΙΑ",
        "sm_greeks_title": "📐 Greeks — τι σημαίνουν",
        "sm_btn_explain_call_long": "Κερδίζεις αν το {sym} ανέβει πάνω από ${be}",
        "sm_btn_explain_call_short": "Κερδίζεις αν το {sym} μείνει κάτω από ${be}",
        "sm_btn_explain_put_long": "Κερδίζεις αν το {sym} πέσει κάτω από ${be}",
        "sm_btn_explain_put_short": "Κερδίζεις αν το {sym} μείνει πάνω από ${be}",
        "sm_contract_note": "1 contract = {size}",
        "sm_contract_crypto": "0.1 {sym}",
        "sm_contract_stock": "100 μετοχές",
        # Stage 26: Save/Load Strategies
        "sl_save_btn": "💾 Αποθήκευση",
        "sl_load_btn": "📂 Στρατηγικές",
        "sl_save_title": "💾 Αποθήκευση Στρατηγικής",
        "sl_save_name": "Όνομα στρατηγικής:",
        "sl_save_placeholder": "π.χ. Covered Call BTC",
        "sl_save_confirm": "✅ Αποθήκευση",
        "sl_save_cancel": "Ακύρωση",
        "sl_save_empty": "⚠️ Δεν έχεις legs για αποθήκευση.",
        "sl_save_no_name": "⚠️ Γράψε ένα όνομα.",
        "sl_saved": "✅ Αποθηκεύτηκε!",
        "sl_load_title": "📂 Αποθηκευμένες Στρατηγικές",
        "sl_load_empty": "Δεν έχεις αποθηκευμένες στρατηγικές ακόμα.",
        "sl_load_hint": "Πάτα μία για να τη φορτώσεις.",
        "sl_load_btn_action": "Φόρτωση",
        "sl_delete_btn_action": "Διαγραφή",
        "sl_legs_count": "legs",
        "sl_confirm_delete": "Σίγουρα;",
        "sl_saved_at": "Αποθηκεύτηκε",
    },
    "en": {
        "title": "Options Dashboard",
        "subtitle": "Crypto & stocks options analytics",
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
        "iv_btn": "📈 IV Chart",
        "iv_chart_title": "📈 IV per Strike (Volatility Smile)",
        "guide_title": "📖 Strategy Guide",
        "analysis_title": "📊 Strategy Analysis",
        "iv_title": "📈 Volatility Smile",
        "analysis_no_legs": "⚠️ No legs. Click a row + **+ LONG / + SHORT** or pick a preset.",
        "analysis_your_legs": "🎯 Your legs",
        "analysis_chart": "📈 Profit / Loss Chart",
        "analysis_scenarios": "🎲 All Scenarios",
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
        "outcomes_prob": "prob",
        "even_title": "📍 Break-even Points",
        "even_vs_usd": "Even vs full USD",
        "even_vs_crypto": "Even vs full BTC",
        "even_vs_stock": "Even vs full shares",
        "min_position": "Minimum position",
        "outcome_above": "If {sym} ≥ ${strike}",
        "outcome_below": "If {sym} < ${strike}",
        "outcome_between": "If ${lo} ≤ {sym} < ${hi}",
        "strike_modal_title": "🔍 Strike Analysis",
        "analytics_table": "📊 Option Details",
        "call_chart_title": "📈 CALL Payoff (Long)",
        "put_chart_title": "📉 PUT Payoff (Long)",
        "add_call_long": "🟢 BUY CALL",
        "add_call_short": "🔴 SELL CALL",
        "add_put_long": "🟢 BUY PUT",
        "add_put_short": "🔴 SELL PUT",
        "field": "Field",
        "call_label": "🔵 CALL",
        "put_label": "🔴 PUT",
        "strike_label": "Strike",
        "premium_label": "Premium",
        "capital_label": "Capital",
        "prob_itm_label": "Prob ITM",
        "break_even_label": "Break-even",
        "iv_calls": "Calls IV",
        "iv_puts": "Puts IV",
        "iv_spot": "Spot",
        "iv_strike": "Strike",
        "iv_iv": "IV (%)",
        "iv_no_data": "⚠️ No IV data for this expiry.",
        "iv_hint": "The Volatility Smile shows how IV changes per strike. Low near spot, high at the wings.",
        # Stage 24: Educational Strike Modal
        "sm_what_is": "📖 What is this option?",
        "sm_what_is_call": "A CALL option with strike **${strike}** gives you the **right** (not obligation) to **BUY** {sym} at **${strike}** until expiry. You profit when {sym} rises above **${breakeven}**.",
        "sm_what_is_put": "A PUT option with strike **${strike}** gives you the **right** (not obligation) to **SELL** {sym} at **${strike}** until expiry. You profit when {sym} falls below **${breakeven}**.",
        "sm_current_status": "📍 Current status",
        "sm_spot_now": "Spot now",
        "sm_moneyness": "Status",
        "sm_moneyness_itm": "🟢 ITM (In The Money) — has intrinsic value",
        "sm_moneyness_atm": "🟡 ATM (At The Money) — at strike",
        "sm_moneyness_otm": "🔴 OTM (Out of The Money) — no intrinsic value",
        "sm_moneyness_itm_short": "ITM",
        "sm_moneyness_atm_short": "ATM",
        "sm_moneyness_otm_short": "OTM",
        "sm_intrinsic": "Intrinsic value",
        "sm_time_value": "Time value",
        "sm_breakeven_short": "Break-even",
        "sm_breakeven_explain": "The price where you neither win nor lose",
        "sm_table_title": "📊 Data table",
        "sm_tooltip_strike": "The price at which you can buy/sell the underlying",
        "sm_tooltip_bid": "The price someone is willing to BUY the option",
        "sm_tooltip_ask": "The price someone is willing to SELL the option",
        "sm_tooltip_premium": "Mid price (Bid + Ask) / 2 — what you usually pay",
        "sm_tooltip_iv": "Implied Volatility — how volatile the market expects {sym} to be",
        "sm_tooltip_delta": "How much the option price changes if {sym} moves $1",
        "sm_tooltip_prob": "Probability (Black-Scholes) the option expires ITM",
        "sm_tooltip_capital": "How much money you need for 1 contract ({size})",
        "sm_interp_title": "💡 What does this mean for me?",
        "sm_interp_cheap": "Premium is **low** (${prem}). Cheap but with small chance of profit ({prob}%).",
        "sm_interp_expensive": "Premium is **high** (${prem}). Expensive but with high chance of profit ({prob}%).",
        "sm_interp_mid": "Premium is **moderate** (${prem}) with {prob}% chance of profit.",
        "sm_interp_bullish": "If you think {sym} will **RISE** → consider **BUY CALL**.",
        "sm_interp_bearish": "If you think {sym} will **FALL** → consider **BUY PUT**.",
        "sm_interp_neutral": "If you think it will stay **flat** → consider **SELLING** options (short).",
        "sm_example_title": "🎯 Example (BUY CALL)",
        "sm_example_up": "If {sym} goes to **${price}** at expiry:",
        "sm_example_down": "If {sym} stays at **${price}** at expiry:",
        "sm_example_payoff": "Payoff",
        "sm_example_cost": "Cost",
        "sm_example_result": "Result",
        "sm_example_win": "PROFIT",
        "sm_example_lose": "LOSS",
        "sm_greeks_title": "📐 Greeks — what they mean",
        "sm_btn_explain_call_long": "You profit if {sym} rises above ${be}",
        "sm_btn_explain_call_short": "You profit if {sym} stays below ${be}",
        "sm_btn_explain_put_long": "You profit if {sym} falls below ${be}",
        "sm_btn_explain_put_short": "You profit if {sym} stays above ${be}",
        "sm_contract_note": "1 contract = {size}",
        "sm_contract_crypto": "0.1 {sym}",
        "sm_contract_stock": "100 shares",
        # Stage 26: Save/Load Strategies
        "sl_save_btn": "💾 Save",
        "sl_load_btn": "📂 Strategies",
        "sl_save_title": "💾 Save Strategy",
        "sl_save_name": "Strategy name:",
        "sl_save_placeholder": "e.g. BTC Covered Call",
        "sl_save_confirm": "✅ Save",
        "sl_save_cancel": "Cancel",
        "sl_save_empty": "⚠️ No legs to save.",
        "sl_save_no_name": "⚠️ Enter a name.",
        "sl_saved": "✅ Saved!",
        "sl_load_title": "📂 Saved Strategies",
        "sl_load_empty": "No saved strategies yet.",
        "sl_load_hint": "Click one to load it.",
        "sl_load_btn_action": "Load",
        "sl_delete_btn_action": "Delete",
        "sl_legs_count": "legs",
        "sl_confirm_delete": "Sure?",
        "sl_saved_at": "Saved",
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
CRYPTO_CONTRACT = 0.1
STOCK_CONTRACT = 100

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
        return {"delta": round(delta, 4), "gamma": round(gamma, 6),
                "theta": round(theta, 4), "vega": round(vega, 4)}
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
        return max((exp - now).total_seconds() / (365.0 * 24 * 3600), 0.0)
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

def get_crypto_chain(currency, expiry_label, limit=200):
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

        capital_long = ask_usd * CRYPTO_CONTRACT if ask_usd else None

        rows.append({
            "instrument": name, "type": opt_type, "strike": strike,
            "bid": bid_usd, "ask": ask_usd,
            "premium": round(premium, 2) if premium else None,
            "capital": round(capital_long, 2) if capital_long else None,
            "prob_itm": round(prob, 4) if prob is not None else None,
            "iv_value": iv_dec,
            "delta": greeks["delta"], "gamma": greeks["gamma"],
            "theta": greeks["theta"], "vega": greeks["vega"],
            "iv": iv_pct,
            "volume": item.get("volume"), "oi": item.get("open_interest"),
        })
    cache_set(key, rows, ttl=60)
    return rows


def _parse_deribit_expiry_to_years(label):
    try:
        day = int(label[:2]); mon_str = label[2:5]; year = int("20" + label[5:7])
        months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]
        month = months.index(mon_str) + 1
        exp = datetime(year, month, day, 8, 0, 0, tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        return max((exp - now).total_seconds() / (365.0 * 24 * 3600), 0.0)
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
        if v is None: return 0.0
        f = float(v)
        if f != f: return 0.0
        return f
    except Exception:
        return 0.0


def get_stock_chain(symbol, expiry, max_strikes=200):
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
        bid = round(last * 0.98, 2); ask = round(last * 1.02, 2)

    if iv < 0.001:
        iv_dec = 0; iv_pct = 0
    else:
        iv_dec = iv; iv_pct = iv * 100

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
        "type": opt_type, "strike": strike, "bid": bid, "ask": ask,
        "premium": round(premium, 2),
        "capital": round(capital, 2) if capital else None,
        "prob_itm": round(prob, 4) if prob is not None else None,
        "iv_value": iv_dec,
        "delta": greeks["delta"], "gamma": greeks["gamma"],
        "theta": greeks["theta"], "vega": greeks["vega"],
        "iv": iv_pct, "volume": int(volume),
        "oi": int(_clean(r.get("openInterest"))),
    }

def _make_vol_renderer():
    """JS cellRenderer for VOL column — bar + number."""
    return {
        "function": """
        function(params) {
            var val = params.value || 0;
            var max = params.api.getColumnDef('volume')?.cellRendererParams?.max || 1000;
            var pct = Math.min(100, (val / max) * 100);
            var div = document.createElement('div');
            div.className = 'vol-bar-cell';
            var bar = document.createElement('div');
            bar.className = 'vol-bar-fill';
            bar.style.width = pct + '%';
            var span = document.createElement('span');
            span.className = 'vol-value';
            span.textContent = val.toLocaleString();
            div.appendChild(bar);
            div.appendChild(span);
            return div;
        }
        """
    }


def _make_oi_renderer():
    """JS cellRenderer for OI column — bar + number."""
    return {
        "function": """
        function(params) {
            var val = params.value || 0;
            var max = params.api.getColumnDef('oi')?.cellRendererParams?.max || 1000;
            var pct = Math.min(100, (val / max) * 100);
            var div = document.createElement('div');
            div.className = 'oi-bar-cell';
            var bar = document.createElement('div');
            bar.className = 'oi-bar-fill';
            bar.style.width = pct + '%';
            var span = document.createElement('span');
            span.className = 'oi-value';
            span.textContent = val.toLocaleString();
            div.appendChild(bar);
            div.appendChild(span);
            return div;
        }
        """
    }


def _make_vol_renderer():
    """JS cellRenderer for VOL column — bar + number."""
    return {
        "function": """
        function(params) {
            var val = params.value || 0;
            var max = params.cellRendererParams?.max || 1000;
            var pct = Math.min(100, (val / max) * 100);
            var div = document.createElement('div');
            div.className = 'vol-bar-cell';
            var bar = document.createElement('div');
            bar.className = 'vol-bar-fill';
            bar.style.width = pct + '%';
            var span = document.createElement('span');
            span.className = 'vol-value';
            span.textContent = val.toLocaleString();
            div.appendChild(bar);
            div.appendChild(span);
            return div;
        }
        """
    }


def _make_oi_renderer():
    """JS cellRenderer for OI column — bar + number."""
    return {
        "function": """
        function(params) {
            var val = params.value || 0;
            var max = params.cellRendererParams?.max || 1000;
            var pct = Math.min(100, (val / max) * 100);
            var div = document.createElement('div');
            div.className = 'oi-bar-cell';
            var bar = document.createElement('div');
            bar.className = 'oi-bar-fill';
            bar.style.width = pct + '%';
            var span = document.createElement('span');
            span.className = 'oi-value';
            span.textContent = val.toLocaleString();
            div.appendChild(bar);
            div.appendChild(span);
            return div;
        }
        """
    }


def build_chain_view(rows, spot=None):
    by_strike = {}
    for r in rows:
        k = r["strike"]
        if k not in by_strike:
            by_strike[k] = {"strike": k}
        if r["type"] == "call":
            by_strike[k]["call"] = r
        elif r["type"] == "put":
            by_strike[k]["put"] = r

    chain_rows = []
    for k in sorted(by_strike.keys()):
        entry = by_strike[k]
        c = entry.get("call"); p = entry.get("put")
        c_vol = (c.get("volume") or 0) if c else 0
        p_vol = (p.get("volume") or 0) if p else 0
        c_oi = (c.get("oi") or 0) if c else 0
        p_oi = (p.get("oi") or 0) if p else 0
        chain_rows.append({
            "strike": k,
            "distance": abs(k - spot) if spot else k,
            "c_bid": c.get("bid") if c else None,
            "c_ask": c.get("ask") if c else None,
            "c_iv": c.get("iv") if c else None,
            "c_delta": c.get("delta") if c else None,
            "c_instrument": c.get("instrument") if c else None,
            "p_bid": p.get("bid") if p else None,
            "p_ask": p.get("ask") if p else None,
            "p_iv": p.get("iv") if p else None,
            "p_delta": p.get("delta") if p else None,
            "p_instrument": p.get("instrument") if p else None,
            "volume": round(c_vol + p_vol, 1),
            "oi": round(c_oi + p_oi, 1),
            "chart_btn": "📊",
        })

    if spot:
        chain_rows.sort(key=lambda r: r["distance"])
    return chain_rows


# ============================================================
# ANALYTICS
# ============================================================
def analyze_strategy(spot, legs, symbol, lang, chain_rows=None):
    if not legs:
        return None
    s = STRINGS[lang]
    is_crypto = symbol in CRYPTO_SYMBOLS
    multiplier = CRYPTO_CONTRACT if is_crypto else STOCK_CONTRACT

    strikes = [l["strike"] for l in legs if l["type"] != "underlying"]
    all_levels = strikes + [spot] if strikes else [spot]
    low = min(all_levels) * 0.80; high = max(all_levels) * 1.20
    step = (high - low) / 200
    prices = [low + i * step for i in range(201)]

    def payoff(p):
        pnl = 0.0
        for leg in legs:
            side = leg["side"]; prem = leg["premium"]
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
                breakevens.append(round(x0 - y0 * (x1 - x0) / (y1 - y0), 2))

    max_profit = max(pnls); max_loss = min(pnls)

    win_ranges = []
    in_win = False; win_start = None
    for i, pnl in enumerate(pnls):
        if pnl > 0 and not in_win:
            in_win = True; win_start = prices[i]
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

    exec_steps = []
    capital_usd = 0.0; capital_crypto = 0.0
    for leg in legs:
        if leg["type"] == "underlying":
            qty = multiplier
            cost = spot * qty * leg["side"]
            action = "BUY" if leg["side"] > 0 else "SELL"
            desc = (f"{qty} {leg['instrument']} @ ${spot:,.2f}" if is_crypto
                    else f"{int(qty)} shares {leg['instrument']} @ ${spot:,.2f}")
            exec_steps.append({"action": action, "desc": desc, "cost": cost})
            if leg["side"] > 0:
                capital_usd += abs(cost)
                if is_crypto:
                    capital_crypto += qty
        else:
            qty = multiplier
            cost = leg["premium"] * qty * leg["side"]
            action = "BUY" if leg["side"] > 0 else "SELL"
            opt_desc = (f"1 {leg['type'].upper()} K=${leg['strike']:,.0f} (0.1 BTC) @ ${leg['premium']:,.2f}"
                        if is_crypto
                        else f"1 {leg['type'].upper()} K=${leg['strike']:,.0f} (100 shares) @ ${leg['premium']:,.2f}")
            exec_steps.append({"action": action, "desc": opt_desc, "cost": cost})
            if leg["side"] > 0:
                capital_usd += abs(cost)

    outcomes = []
    has_underlying_long = any(l["type"] == "underlying" and l["side"] > 0 for l in legs)
    short_calls = [l for l in legs if l["type"] == "call" and l["side"] < 0]
    long_calls = [l for l in legs if l["type"] == "call" and l["side"] > 0]
    short_puts = [l for l in legs if l["type"] == "put" and l["side"] < 0]
    long_puts = [l for l in legs if l["type"] == "put" and l["side"] > 0]

    if has_underlying_long and len(short_calls) == 1 and not long_calls and not short_puts and not long_puts:
        sc = short_calls[0]; k = sc["strike"]
        prem_btc = sc["premium"] / spot if spot else 0
        o_above = payoff(k * 1.01)
        pct = (o_above / capital_usd * 100) if capital_usd else 0
        outcomes.append({"label": s["outcome_above"].format(sym=symbol, strike=f"{k:,.0f}"),
                         "pnl_usd": o_above, "pnl_pct": pct, "prob": 0.35})
        o_below = prem_btc * spot * multiplier
        pct = (o_below / capital_usd * 100) if capital_usd else 0
        outcomes.append({"label": s["outcome_below"].format(sym=symbol, strike=f"{k:,.0f}"),
                         "pnl_usd": o_below, "pnl_pct": pct, "prob": 0.65})
    elif len(long_calls) == 1 and len(short_calls) == 1 and not has_underlying_long:
        lc = long_calls[0]; sc = short_calls[0]
        lo = min(lc["strike"], sc["strike"]); hi = max(lc["strike"], sc["strike"])
        above = payoff(hi * 1.01); below = payoff(lo * 0.99); mid = payoff((lo + hi) / 2)
        outcomes.append({"label": s["outcome_above"].format(sym=symbol, strike=f"{hi:,.0f}"),
                         "pnl_usd": above, "pnl_pct": (above/abs(net_cost)*100) if net_cost else 0, "prob": 0.4})
        outcomes.append({"label": s["outcome_between"].format(lo=f"{lo:,.0f}", hi=f"{hi:,.0f}", sym=symbol),
                         "pnl_usd": mid, "pnl_pct": (mid/abs(net_cost)*100) if net_cost else 0, "prob": 0.3})
        outcomes.append({"label": s["outcome_below"].format(sym=symbol, strike=f"{lo:,.0f}"),
                         "pnl_usd": below, "pnl_pct": (below/abs(net_cost)*100) if net_cost else 0, "prob": 0.3})
    elif len(short_calls) == 1 and len(long_calls) == 1 and len(short_puts) == 1 and len(long_puts) == 1:
        sc = short_calls[0]; lc = long_calls[0]; sp = short_puts[0]; lp = long_puts[0]
        mid = payoff((sp["strike"] + sc["strike"]) / 2)
        above = payoff(max(sc["strike"], lc["strike"]) * 1.01)
        below = payoff(min(sp["strike"], lp["strike"]) * 0.99)
        outcomes.append({"label": s["outcome_between"].format(lo=f"{sp['strike']:,.0f}", hi=f"{sc['strike']:,.0f}", sym=symbol),
                         "pnl_usd": mid, "pnl_pct": (mid/abs(net_cost)*100) if net_cost else 0, "prob": 0.5})
        outcomes.append({"label": s["outcome_above"].format(sym=symbol, strike=f"{max(sc['strike'], lc['strike']):,.0f}"),
                         "pnl_usd": above, "pnl_pct": (above/abs(net_cost)*100) if net_cost else 0, "prob": 0.25})
        outcomes.append({"label": s["outcome_below"].format(sym=symbol, strike=f"{min(sp['strike'], lp['strike']):,.0f}"),
                         "pnl_usd": below, "pnl_pct": (below/abs(net_cost)*100) if net_cost else 0, "prob": 0.25})
    elif len(long_calls) == 1 and len(long_puts) == 1 and not short_calls and not short_puts:
        lc = long_calls[0]; strike = lc["strike"]
        up = payoff(strike * 1.05); down = payoff(strike * 0.95); mid = payoff(strike)
        outcomes.append({"label": s["outcome_above"].format(sym=symbol, strike=f"{strike*1.05:,.0f}"),
                         "pnl_usd": up, "pnl_pct": (up/abs(net_cost)*100) if net_cost else 0, "prob": 0.35})
        outcomes.append({"label": s["outcome_below"].format(sym=symbol, strike=f"{strike*0.95:,.0f}"),
                         "pnl_usd": down, "pnl_pct": (down/abs(net_cost)*100) if net_cost else 0, "prob": 0.35})
        outcomes.append({"label": f"{symbol} ≈ ${strike:,.0f}",
                         "pnl_usd": mid, "pnl_pct": (mid/abs(net_cost)*100) if net_cost else 0, "prob": 0.30})

    even_vs = {}
    if has_underlying_long and len(short_calls) == 1:
        sc = short_calls[0]
        even_vs["usd"] = round(sc["strike"] - sc["premium"], 2)
        even_vs["crypto"] = round(sc["strike"] + sc["premium"], 2)

    warnings = []
    if even_vs:
        k = even_vs.get("usd"); up = even_vs.get("crypto")
        if k:
            warnings.append({"text": f"{s['warn_below']} ${k:,.2f} ({(k/spot-1)*100:+.1f}%), {s['warn_less_usd']}"})
        if up:
            warn_less = s["warn_less_crypto"] if is_crypto else s["warn_less_stock"]
            warnings.append({"text": f"{s['warn_above']} ${up:,.2f} ({(up/spot-1)*100:+.1f}%), {warn_less}"})

    return {
        "chart": fig, "scenarios": scenarios,
        "net_cost": round(net_cost, 2),
        "max_profit": max_profit, "max_loss": max_loss,
        "breakevens": breakevens, "win_ranges": win_ranges,
        "spot": spot, "legs": legs,
        "exec_steps": exec_steps,
        "capital_usd": round(capital_usd, 2),
        "capital_crypto": round(capital_crypto, 6),
        "outcomes": outcomes, "even_vs": even_vs, "warnings": warnings,
        "multiplier": multiplier, "is_crypto": is_crypto,
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


def make_single_option_chart(spot, strike, premium, opt_type, symbol, contract_size):
    low = strike * 0.80
    high = strike * 1.20
    step = (high - low) / 100
    prices = [low + i * step for i in range(101)]

    payoffs = []
    for p in prices:
        if opt_type == "call":
            intrinsic = max(p - strike, 0)
        else:
            intrinsic = max(strike - p, 0)
        pnl = (intrinsic - premium) * contract_size
        payoffs.append(pnl)

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
                             fill="tozeroy", fillcolor="rgba(46, 204, 113, 0.20)",
                             name="Profit"))
    fig.add_trace(go.Scatter(x=loss_x, y=loss_y, mode="lines",
                             line=dict(color=LOSS, width=3),
                             fill="tozeroy", fillcolor="rgba(231, 76, 60, 0.20)",
                             name="Loss"))
    fig.add_hline(y=0, line_dash="dash", line_color="#8b949e")
    fig.add_vline(x=strike, line_dash="dot", line_color=STRIKE, line_width=2,
                  annotation_text=f"K=${strike:,.0f}", annotation_position="top right",
                  annotation_font=dict(color=STRIKE, size=10))
    fig.add_vline(x=spot, line_dash="dot", line_color=SPOT, line_width=2,
                  annotation_text=f"Spot ${spot:,.0f}", annotation_position="bottom left",
                  annotation_font=dict(color=SPOT, size=10))

    fig.update_layout(
        paper_bgcolor="#161b22", plot_bgcolor="#161b22",
        font=dict(color="#e6edf3", size=10),
        xaxis=dict(title=dict(text=f"{symbol} Price at Expiry", font=dict(color="#e6edf3", size=10)),
                   tickfont=dict(color="#8b949e", size=9), gridcolor="#30363d",
                   tickprefix="$", tickformat=",.0f"),
        yaxis=dict(title=dict(text="P&L ($)", font=dict(color="#e6edf3", size=10)),
                   tickfont=dict(color="#8b949e", size=9), gridcolor="#30363d",
                   tickprefix="$", tickformat=",.0f"),
        margin=dict(l=60, r=20, t=30, b=40),
        height=320,
        showlegend=False,
    )
    return fig


def make_iv_chart(rows, spot, symbol, lang):
    s = STRINGS[lang]
    by_strike = {}
    for r in rows:
        k = r.get("strike")
        iv = r.get("iv")
        if k is None or iv is None:
            continue
        if k not in by_strike:
            by_strike[k] = iv

    strikes = sorted(by_strike.keys())
    ivs = [by_strike[k] for k in strikes]

    fig = go.Figure()

    if strikes:
        fig.add_trace(go.Scatter(
            x=strikes,
            y=ivs,
            mode="lines+markers",
            name=s["iv_title"],
            line=dict(color=ACCENT, width=3),
            marker=dict(size=10, color=STRIKE, line=dict(color=ACCENT, width=2)),
            hovertemplate="Strike: $%{x:,.0f}<br>IV: %{y:.2f}%<extra></extra>",
        ))

    fig.add_vline(x=spot, line_dash="dot", line_color=SPOT, line_width=2,
                  annotation_text=f"{s['iv_spot']} ${spot:,.0f}",
                  annotation_position="top",
                  annotation_font=dict(color=SPOT, size=11))

    fig.update_layout(
        paper_bgcolor="#161b22", plot_bgcolor="#161b22",
        font=dict(color="#e6edf3", size=11),
        xaxis=dict(
            title=dict(text=s["iv_strike"], font=dict(color="#e6edf3")),
            tickfont=dict(color="#8b949e"), gridcolor="#30363d",
            tickprefix="$", tickformat=",.0f",
        ),
        yaxis=dict(
            title=dict(text=s["iv_iv"], font=dict(color="#e6edf3")),
            tickfont=dict(color="#8b949e"), gridcolor="#30363d",
            ticksuffix="%",
        ),
        margin=dict(l=60, r=30, t=40, b=50),
        hovermode="x unified",
        showlegend=False,
        height=420,
    )
    return fig


# ============================================================
# STAGE 24: Single Option Analysis Helper
# ============================================================
def _analyze_single_option(spot, strike, opt_type, premium, iv_pct, is_crypto):
    contract_size = CRYPTO_CONTRACT if is_crypto else STOCK_CONTRACT
    premium_usd = premium or 0

    diff = spot - strike
    threshold = spot * 0.005
    if abs(diff) < threshold:
        moneyness = "atm"
    elif opt_type == "call":
        moneyness = "itm" if spot > strike else "otm"
    else:
        moneyness = "itm" if spot < strike else "otm"

    if opt_type == "call":
        intrinsic = max(spot - strike, 0)
        breakeven = strike + premium_usd
    else:
        intrinsic = max(strike - spot, 0)
        breakeven = strike - premium_usd

    time_value = max(premium_usd - intrinsic, 0)
    total_cost = premium_usd * contract_size

    if opt_type == "call":
        up_price = strike * 1.05
        down_price = spot * 0.98
    else:
        up_price = strike * 0.95
        down_price = spot * 1.02

    def _payoff_long(p):
        if opt_type == "call":
            return (max(p - strike, 0) - premium_usd) * contract_size
        else:
            return (max(strike - p, 0) - premium_usd) * contract_size

    example_up = {"price": up_price, "pnl": _payoff_long(up_price)}
    example_down = {"price": down_price, "pnl": _payoff_long(down_price)}

    return {
        "moneyness": moneyness,
        "intrinsic": round(intrinsic, 2),
        "time_value": round(time_value, 2),
        "breakeven": round(breakeven, 2),
        "total_cost": round(total_cost, 2),
        "example_up": example_up,
        "example_down": example_down,
        "contract_size": contract_size,
    }

app = Dash(__name__)
server = app.server

           



app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Options Dashboard</title>
        {%favicon%}
        {%css%}
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
        <style>
            * { box-sizing: border-box; }
            body { margin: 0; -webkit-font-smoothing: antialiased; }

            .ds-btn, .ds-symbol, .ds-expiry, .ds-preset, .ds-action, .ds-filter, .ds-theme {
                font-family: 'Inter', -apple-system, sans-serif;
                cursor: pointer;
                transition: all 0.18s cubic-bezier(0.4, 0, 0.2, 1);
                display: inline-flex;
                align-items: center;
                gap: 6px;
                white-space: nowrap;
                letter-spacing: -0.01em;
            }
            .ds-btn:hover, .ds-symbol:hover, .ds-expiry:hover,
            .ds-preset:hover, .ds-action:hover, .ds-filter:hover {
                transform: translateY(-1px);
                filter: brightness(1.12);
            }
            .ds-symbol {
                padding: 9px 16px; margin-right: 6px; margin-bottom: 6px;
                border-radius: 8px; font-size: 13px; font-weight: 600;
            }
            .ds-expiry {
                padding: 7px 13px; margin-right: 6px; margin-bottom: 6px;
                border-radius: 7px; font-size: 11px; font-weight: 600;
                letter-spacing: 0.02em;
            }
            .ds-preset {
                padding: 9px 15px; margin-right: 8px; margin-bottom: 6px;
                border-radius: 8px; font-size: 12px; font-weight: 600;
            }
            .ds-action {
                padding: 7px 13px; margin-left: 6px;
                border-radius: 7px; font-size: 11px; font-weight: 700;
            }
            .ds-filter {
                padding: 6px 13px; margin-left: 6px;
                border-radius: 7px; font-size: 11px; font-weight: 700;
            }
            .ds-theme {
                font-size: 15px; padding: 8px 12px; border-radius: 8px;
                font-weight: 600;
            }

            .ag-theme-alpine-dark {
                --ag-background-color: #0d1117;
                --ag-header-background-color: #161b22;
                --ag-odd-row-background-color: #0d1117;
                --ag-even-row-background-color: #11161d;
                --ag-row-hover-color: #1c2128;
                --ag-border-color: #21262d;
                --ag-foreground-color: #e6edf3;
                --ag-header-foreground-color: #8b949e;
                --ag-selected-row-background-color: rgba(31, 111, 235, 0.15);
                --ag-font-size: 12px;
                --ag-font-family: 'JetBrains Mono', 'SF Mono', monospace;
                --ag-header-height: 38px;
                --ag-row-height: 34px;
            }
            .ag-theme-alpine {
                --ag-background-color: #ffffff;
                --ag-header-background-color: #f6f8fa;
                --ag-odd-row-background-color: #ffffff;
                --ag-even-row-background-color: #fafbfc;
                --ag-row-hover-color: #f3f4f6;
                --ag-border-color: #e5e7eb;
                --ag-foreground-color: #1f2328;
                --ag-header-foreground-color: #57606a;
                --ag-selected-row-background-color: rgba(31, 111, 235, 0.08);
                --ag-font-size: 12px;
                --ag-font-family: 'JetBrains Mono', 'SF Mono', monospace;
                --ag-header-height: 38px;
                --ag-row-height: 34px;
            }

            .ag-theme-alpine-dark .ag-header-cell-text,
            .ag-theme-alpine .ag-header-cell-text {
                font-weight: 700 !important;
                text-transform: uppercase;
                font-size: 10px !important;
                letter-spacing: 0.08em;
                font-family: 'Inter', sans-serif !important;
            }
            .ag-theme-alpine-dark .ag-header-cell[col-id^="c_"],
            .ag-theme-alpine .ag-header-cell[col-id^="c_"] {
                background: rgba(46, 204, 113, 0.06) !important;
            }
            .ag-theme-alpine-dark .ag-header-cell[col-id^="p_"],
            .ag-theme-alpine .ag-header-cell[col-id^="p_"] {
                background: rgba(231, 76, 60, 0.06) !important;
            }
            .ag-theme-alpine-dark .ag-header-cell[col-id="strike"],
            .ag-theme-alpine .ag-header-cell[col-id="strike"] {
                background: rgba(243, 156, 18, 0.12) !important;
                font-weight: 800 !important;
                color: #f39c12 !important;
            }
            .ag-theme-alpine-dark .ag-cell,
            .ag-theme-alpine .ag-cell {
                font-family: 'JetBrains Mono', 'SF Mono', monospace !important;
                font-size: 12px !important;
                letter-spacing: -0.01em;
            }
             /* ============ HEADER COLORS ============ */
            .ag-theme-alpine-dark .ag-header-cell[col-id="c_bid"],
            .ag-theme-alpine .ag-header-cell[col-id="c_bid"],
            .ag-theme-alpine-dark .ag-header-cell[col-id="p_bid"],
            .ag-theme-alpine .ag-header-cell[col-id="p_bid"] {
                background: rgba(46, 204, 113, 0.15) !important;
            }
            .ag-theme-alpine-dark .ag-header-cell[col-id="c_ask"],
            .ag-theme-alpine .ag-header-cell[col-id="c_ask"],
            .ag-theme-alpine-dark .ag-header-cell[col-id="p_ask"],
            .ag-theme-alpine .ag-header-cell[col-id="p_ask"] {
                background: rgba(231, 76, 60, 0.15) !important;
            }
            .ag-theme-alpine-dark .ag-header-cell[col-id="c_iv"],
            .ag-theme-alpine .ag-header-cell[col-id="c_iv"],
            .ag-theme-alpine-dark .ag-header-cell[col-id="p_iv"],
            .ag-theme-alpine .ag-header-cell[col-id="p_iv"] {
                background: rgba(243, 156, 18, 0.15) !important;
            }
            .ag-theme-alpine-dark .ag-header-cell[col-id="c_delta"],
            .ag-theme-alpine .ag-header-cell[col-id="c_delta"],
            .ag-theme-alpine-dark .ag-header-cell[col-id="p_delta"],
            .ag-theme-alpine .ag-header-cell[col-id="p_delta"] {
                background: rgba(155, 89, 182, 0.15) !important;
            }
            .ag-theme-alpine-dark .ag-header-cell[col-id="volume"],
            .ag-theme-alpine .ag-header-cell[col-id="volume"] {
                background: rgba(46, 204, 113, 0.2) !important;
            }
            .ag-theme-alpine-dark .ag-header-cell[col-id="oi"],
            .ag-theme-alpine .ag-header-cell[col-id="oi"] {
                background: rgba(88, 166, 255, 0.2) !important;
            }
            .ag-theme-alpine-dark .ag-header-cell[col-id="strike"],
            .ag-theme-alpine .ag-header-cell[col-id="strike"] {
                background: rgba(243, 156, 18, 0.25) !important;
            }
            .ag-theme-alpine-dark .ag-header-cell[col-id="chart_btn"],
            .ag-theme-alpine .ag-header-cell[col-id="chart_btn"] {
                background: rgba(139, 148, 158, 0.15) !important;
            }
            /* ============ CENTER ALIGN ============ */
            .ag-theme-alpine-dark .ag-header-cell-label,
            .ag-theme-alpine .ag-header-cell-label {
                justify-content: center !important;
            }
            .ag-theme-alpine-dark .ag-header-cell-comp-wrapper,
            .ag-theme-alpine .ag-header-cell-comp-wrapper {
                justify-content: center !important;
            }
            .ag-theme-alpine-dark .ag-cell,
            .ag-theme-alpine .ag-cell {
                text-align: center !important;
            }
            /* ============ COLUMN COLORS ============ */
            .ag-theme-alpine-dark .ag-cell[col-id="c_bid"],
            .ag-theme-alpine .ag-cell[col-id="c_bid"],
            .ag-theme-alpine-dark .ag-cell[col-id="p_bid"],
            .ag-theme-alpine .ag-cell[col-id="p_bid"] {
                color: #2ecc71 !important;
                font-weight: 600;
            }
            .ag-theme-alpine-dark .ag-cell[col-id="c_ask"],
            .ag-theme-alpine .ag-cell[col-id="c_ask"],
            .ag-theme-alpine-dark .ag-cell[col-id="p_ask"],
            .ag-theme-alpine .ag-cell[col-id="p_ask"] {
                color: #e74c3c !important;
                font-weight: 600;
            }
            .ag-theme-alpine-dark .ag-cell[col-id="c_iv"],
            .ag-theme-alpine .ag-cell[col-id="c_iv"],
            .ag-theme-alpine-dark .ag-cell[col-id="p_iv"],
            .ag-theme-alpine .ag-cell[col-id="p_iv"] {
                color: #f39c12 !important;
                font-weight: 600;
            }
            .ag-theme-alpine-dark .ag-cell[col-id="c_delta"],
            .ag-theme-alpine .ag-cell[col-id="c_delta"],
            .ag-theme-alpine-dark .ag-cell[col-id="p_delta"],
            .ag-theme-alpine .ag-cell[col-id="p_delta"] {
                color: #9b59b6 !important;
                font-weight: 600;
            }
            .ag-theme-alpine-dark .ag-cell[col-id="volume"],
            .ag-theme-alpine .ag-cell[col-id="volume"] {
                color: #2ecc71 !important;
                font-weight: 700;
            }
            .ag-theme-alpine-dark .ag-cell[col-id="oi"],
            .ag-theme-alpine .ag-cell[col-id="oi"] {
                color: #58a6ff !important;
                font-weight: 700;
            }
            .ag-theme-alpine-dark .ag-cell[col-id="strike"],
            .ag-theme-alpine .ag-cell[col-id="strike"] {
                color: #f39c12 !important;
                font-weight: 800;
            }
            .ag-theme-alpine-dark .ag-cell[col-id="chart_btn"],
            .ag-theme-alpine .ag-cell[col-id="chart_btn"] {
                cursor: pointer;
                text-align: center;
            }
            .ag-theme-alpine-dark .ag-row-selected {
                background: rgba(31, 111, 235, 0.15) !important;
                border-left: 3px solid #1f6feb !important;
            }
            .ag-theme-alpine .ag-row-selected {
                background: rgba(31, 111, 235, 0.08) !important;
                border-left: 3px solid #1f6feb !important;
            }

            .ds-hint {
                font-size: 11px; color: #8b949e; font-style: italic;
                margin-left: 8px; padding: 3px 10px;
                border-left: 2px solid #30363d;
                font-family: 'Inter', sans-serif;
            }

            .live-price {
                font-size: 20px; font-weight: 700; color: #2ecc71;
                font-family: 'JetBrains Mono', monospace;
                letter-spacing: -0.02em;
                padding: 7px 16px 7px 14px;
                background: rgba(46, 204, 113, 0.08);
                border-radius: 10px;
                border: 1px solid rgba(46, 204, 113, 0.25);
                display: inline-flex; align-items: center; gap: 10px;
                position: relative;
            }
            .live-price .coin-icon {
                font-size: 20px; font-weight: 900; color: #f39c12;
                line-height: 1;
            }
            .live-price .live-dot {
                display: inline-block;
                width: 7px; height: 7px;
                background: #2ecc71;
                border-radius: 50%;
                box-shadow: 0 0 0 0 rgba(46, 204, 113, 0.7);
                animation: pulse 1.8s infinite;
            }
            @keyframes pulse {
                0%   { box-shadow: 0 0 0 0 rgba(46, 204, 113, 0.6); }
                70%  { box-shadow: 0 0 0 8px rgba(46, 204, 113, 0); }
                100% { box-shadow: 0 0 0 0 rgba(46, 204, 113, 0); }
            }

                        /* ============ VOLUME / OI BARS ============ */
            .vol-bar-cell, .oi-bar-cell {
                display: flex;
                align-items: center;
                gap: 6px;
                width: 100%;
                height: 100%;
                padding: 0 4px;
            }
            .vol-bar-fill {
                height: 6px;
                background: linear-gradient(90deg, #2ecc71, #27ae60);
                border-radius: 3px;
                min-width: 2px;
            }
            .oi-bar-fill {
                height: 6px;
                background: linear-gradient(90deg, #58a6ff, #1f6feb);
                border-radius: 3px;
                min-width: 2px;
            }
            .vol-value, .oi-value {
                font-family: 'JetBrains Mono', monospace;
                font-size: 11px;
                font-weight: 600;
            }
            .vol-value { color: #2ecc71; }
            .oi-value { color: #58a6ff; }

            .exec-card {
                background: rgba(31, 111, 235, 0.06);
                border-left: 3px solid #1f6feb;
                border-radius: 8px; padding: 14px 18px; margin-bottom: 12px;
            }
            .exec-action {
                display: inline-block; font-weight: 700; font-size: 10px;
                padding: 3px 8px; border-radius: 4px;
                margin-right: 8px; letter-spacing: 0.06em;
                text-transform: uppercase;
            }
            .exec-buy  { background: rgba(46, 204, 113, 0.18); color: #2ecc71; }
            .exec-sell { background: rgba(231, 76, 60, 0.18); color: #e74c3c; }

            .warn-card {
                background: rgba(243, 156, 18, 0.08);
                border-left: 3px solid #f39c12;
                border-radius: 8px; padding: 12px 16px;
                margin-bottom: 8px; font-size: 13px;
            }

            .greek-card {
                background: rgba(155, 89, 182, 0.06);
                border-left: 3px solid #9b59b6;
                border-radius: 8px; padding: 14px 18px; margin-bottom: 12px;
            }
            .greek-grid {
                display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px;
            }
            .greek-cell {
                background: rgba(255,255,255,0.03); border-radius: 6px;
                padding: 10px; text-align: center;
            }
            .greek-label {
                font-size: 10px; color: #8b949e; text-transform: uppercase;
                letter-spacing: 0.08em; margin-bottom: 4px; font-weight: 600;
            }
            .greek-value { font-size: 16px; font-weight: 700; color: #9b59b6;
                font-family: 'JetBrains Mono', monospace; }

            .outcome-row {
                display: flex; justify-content: space-between;
                align-items: center; padding: 12px 16px;
                border-bottom: 1px solid #21262d; font-size: 13px;
            }
            .outcome-row:last-child { border-bottom: none; }
            .outcome-label { flex: 2; }
            .outcome-pnl {
                flex: 1; text-align: right; font-weight: 700;
                font-family: 'JetBrains Mono', monospace;
            }
            .outcome-prob { flex: 1; text-align: right; color: #8b949e;
                font-size: 12px; font-family: 'JetBrains Mono', monospace; }

            .analytics-table {
                width: 100%;
                border-collapse: collapse;
                background: #161b22;
                border-radius: 10px;
                overflow: hidden;
                border: 1px solid #21262d;
            }
            .analytics-table th {
                background: #0d1117;
                padding: 11px 12px;
                text-align: left;
                font-size: 10px;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                font-weight: 700;
                border-bottom: 1px solid #21262d;
                font-family: 'Inter', sans-serif;
            }
            .analytics-table td {
                padding: 9px 12px;
                border-bottom: 1px solid #21262d;
                font-size: 12px;
                font-family: 'JetBrains Mono', monospace;
            }
            .analytics-table tr:last-child td { border-bottom: none; }

            .add-btn-grid {
                display: grid !important;
                grid-template-columns: 1fr 1fr !important;
                gap: 10px !important;
                margin-top: 16px !important;
                position: sticky !important;
                bottom: 0 !important;
                background: #161b22 !important;
                padding: 12px 0 !important;
                border-top: 1px solid #21262d !important;
            }
            .add-btn {
                padding: 12px 16px;
                border-radius: 8px;
                border: none;
                cursor: pointer;
                font-size: 13px;
                font-weight: 700;
                transition: all 0.15s ease;
                font-family: 'Inter', sans-serif;
            }
            .add-btn:hover { transform: translateY(-2px); filter: brightness(1.15); }
            .add-btn-long {
                background: rgba(46, 204, 113, 0.12); color: #2ecc71;
                border: 1px solid rgba(46, 204, 113, 0.35);
            }
            .add-btn-short {
                background: rgba(231, 76, 60, 0.12); color: #e74c3c;
                border: 1px solid rgba(231, 76, 60, 0.35);
            }

            /* ============ MOBILE GRID ============ */
            @media (max-width: 900px) {
                .ag-theme-alpine-dark .ag-header-cell[col-id="c_ask"],
                .ag-theme-alpine .ag-header-cell[col-id="c_ask"],
                .ag-theme-alpine-dark .ag-header-cell[col-id="c_iv"],
                .ag-theme-alpine .ag-header-cell[col-id="c_iv"],
                .ag-theme-alpine-dark .ag-header-cell[col-id="c_delta"],
                .ag-theme-alpine .ag-header-cell[col-id="c_delta"],
                .ag-theme-alpine-dark .ag-header-cell[col-id="p_ask"],
                .ag-theme-alpine .ag-header-cell[col-id="p_ask"],
                .ag-theme-alpine-dark .ag-header-cell[col-id="p_iv"],
                .ag-theme-alpine .ag-header-cell[col-id="p_iv"],
                .ag-theme-alpine-dark .ag-header-cell[col-id="p_delta"],
                .ag-theme-alpine .ag-header-cell[col-id="p_delta"],
                .ag-theme-alpine-dark .ag-cell[col-id="c_ask"],
                .ag-theme-alpine .ag-cell[col-id="c_ask"],
                .ag-theme-alpine-dark .ag-cell[col-id="c_iv"],
                .ag-theme-alpine .ag-cell[col-id="c_iv"],
                .ag-theme-alpine-dark .ag-cell[col-id="c_delta"],
                .ag-theme-alpine .ag-cell[col-id="c_delta"],
                .ag-theme-alpine-dark .ag-cell[col-id="p_ask"],
                .ag-theme-alpine .ag-cell[col-id="p_ask"],
                .ag-theme-alpine-dark .ag-cell[col-id="p_iv"],
                .ag-theme-alpine .ag-cell[col-id="p_iv"],
                .ag-theme-alpine-dark .ag-cell[col-id="p_delta"],
                .ag-theme-alpine .ag-cell[col-id="p_delta"] {
                    display: none !important;
                }
                .ag-theme-alpine-dark .ag-cell,
                .ag-theme-alpine .ag-cell {
                    font-size: 11px !important;
                }
            }
            #strike-modal { align-items: center !important; justify-content: center !important; }
            #strike-modal-content {
                max-height: 90vh !important;
                overflow-y: auto !important;
                margin: 0 auto !important;
                scrollbar-width: thin;
            }

            @media (max-width: 900px) {
                #main-grid { grid-template-columns: 1fr !important; }
                #header {
                    flex-direction: column !important;
                    gap: 12px !important;
                    padding: 12px 16px !important;
                }
                #header > div { width: 100% !important; justify-content: center !important; }
                .live-price { font-size: 17px !important; padding: 5px 12px !important; }
                .live-price .coin-icon { font-size: 18px !important; }
                .ds-symbol { padding: 7px 12px !important; font-size: 12px !important; }
                .ds-expiry { padding: 5px 10px !important; font-size: 10px !important; }
                .ds-preset { padding: 7px 10px !important; font-size: 11px !important; }
                .ds-action { padding: 5px 8px !important; font-size: 10px !important; }
                .ds-theme { font-size: 14px !important; padding: 6px 10px !important; }
                .ds-hint { display: none !important; }
                #strike-modal-content { width: 95% !important; padding: 16px !important; }
                .analytics-table td, .analytics-table th {
                    padding: 6px 8px !important; font-size: 11px !important;
                }
                .add-btn { padding: 10px 12px !important; font-size: 11px !important; }
            }

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
                    style={"margin": "0", "fontSize": "20px", "fontWeight": "800",
                           "letterSpacing": "-0.02em"}),
            html.P(id="app-subtitle",
                   style={"margin": "2px 0 0 0", "fontSize": "11px",
                          "letterSpacing": "0.01em", "opacity": "0.7"}),
        ], style={"flex": "1"}),
        html.Div([
            html.Span(id="live-price-display", className="live-price",
                      children=[html.Span("₿", className="coin-icon"),
                                html.Span("Loading..."),
                                html.Span(className="live-dot")]),
        ], style={"flex": "1", "display": "flex", "justifyContent": "center"}),
        html.Div([
            html.Button("🇬🇷 / 🇬🇧", id="lang-toggle", n_clicks=0, className="ds-theme"),
            html.Button("☀️", id="theme-toggle", n_clicks=0, className="ds-theme",
                        style={"marginLeft": "8px"}),
            html.Button(id="about-btn", n_clicks=0, className="ds-preset",
                        style={"marginLeft": "12px"}),
            html.Button(id="analysis-btn", n_clicks=0, className="ds-preset",
                        style={"marginLeft": "8px"}),
        ], style={"flex": "1", "display": "flex", "justifyContent": "flex-end",
                  "alignItems": "center"}),
    ], id="header", style={"display": "flex", "alignItems": "center",
                            "padding": "16px 24px", "gap": "16px"}),

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
        html.Button(
            "🔍 Analyze",
            id="analyze-strike-btn",
            n_clicks=0,
            className="ds-preset",
            style={
                "background": "rgba(243,156,18,0.15)",
                "color": "#f39c12",
                "border": "1px solid rgba(243,156,18,0.5)",
                "fontWeight": "700",
                "marginLeft": "12px",
            },
        ),
        html.Button(
            id="iv-btn",
            n_clicks=0,
            className="ds-preset",
            style={
                "background": "rgba(88,166,255,0.15)",
                "color": "#58a6ff",
                "border": "1px solid rgba(88,166,255,0.5)",
                "fontWeight": "700",
                "marginLeft": "8px",
            },
        ),
        html.Button(
            id="save-strategy-btn",
            n_clicks=0,
            className="ds-preset",
            style={
                "background": "rgba(46,204,113,0.12)",
                "color": "#2ecc71",
                "border": "1px solid rgba(46,204,113,0.4)",
                "fontWeight": "700",
                "marginLeft": "8px",
            },
        ),
        html.Button(
            id="load-strategy-btn",
            n_clicks=0,
            className="ds-preset",
            style={
                "background": "rgba(155,89,182,0.12)",
                "color": "#9b59b6",
                "border": "1px solid rgba(155,89,182,0.4)",
                "fontWeight": "700",
                "marginLeft": "8px",
            },
        ),
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
            ], id="grid-header", style={"padding": "12px 16px"}),

            html.Div([
                html.Div([
                    html.Button(id="add-long-btn", n_clicks=0, className="ds-action"),
                    html.Button(id="add-short-btn", n_clicks=0, className="ds-action"),
                    html.Button("📊 Chart", id="show-chart-btn", n_clicks=0, className="ds-action",
                          style={"background": "rgba(243,156,18,0.15)", "color": "#f39c12",
                                       "border": "1px solid rgba(243,156,18,0.5)"}),
                    html.Span(id="manual-hint", className="ds-hint"),
                ], style={"display": "flex", "alignItems": "center"}),
            ], id="manual-row", style={"padding": "0 16px 12px 16px"}),

            dag.AgGrid(
                id="chain-grid",
                columnDefs=[],
                rowData=[],
                    style={"height": "calc(100vh - 260px)", "minHeight": "500px"},
                className="ag-theme-alpine-dark",
                
                dashGridOptions={
                    "rowSelection": {
                        "mode": "singleRow",
                        "checkboxes": False,
                        "enableClickSelection": True,
                    },
                    "animateRows": False,
                    "suppressCellFocus": True,
                    "defaultColDef": {"sortable": True, "resizable": True},
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

        
    ], id="main-grid", style={
        "display": "grid",
        "gridTemplateColumns": "1fr",
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

    html.Div([
        html.Div([
            html.Div([
                html.Span(id="strike-modal-title",
                          style={"fontWeight": "700", "fontSize": "16px"}),
                html.Button("✕", id="close-strike-btn", n_clicks=0,
                            style={"padding": "4px 10px", "borderRadius": "5px",
                                   "border": "1px solid #30363d", "background": "transparent",
                                   "color": "#e6edf3", "fontSize": "14px", "cursor": "pointer"}),
            ], style={"display": "flex", "justifyContent": "space-between",
                      "alignItems": "center", "marginBottom": "12px"}),
            html.Div(id="strike-modal-body"),
        ], id="strike-modal-content", style={}),
    ], id="strike-modal", style={"display": "none"}),
        html.Div([
        html.Div([
            html.Div([
                html.Span(id="chart-modal-title",
                          style={"fontWeight": "700", "fontSize": "16px"}),
                html.Button("✕", id="close-chart-btn", n_clicks=0,
                            style={"padding": "4px 10px", "borderRadius": "5px",
                                   "border": "1px solid #30363d", "background": "transparent",
                                   "color": "#e6edf3", "fontSize": "14px", "cursor": "pointer"}),
            ], style={"display": "flex", "justifyContent": "space-between",
                      "alignItems": "center", "marginBottom": "12px"}),
            html.Div(id="chart-modal-body"),
        ], id="chart-modal-content", style={}),
    ], id="chart-modal", style={"display": "none"}),

    html.Div([
        html.Div([
            html.Div([
                html.Span(id="iv-modal-title",
                          style={"fontWeight": "700", "fontSize": "16px"}),
                html.Button("✕", id="close-iv-btn", n_clicks=0,
                            style={"padding": "4px 10px", "borderRadius": "5px",
                                   "border": "1px solid #30363d", "background": "transparent",
                                   "color": "#e6edf3", "fontSize": "14px", "cursor": "pointer"}),
            ], style={"display": "flex", "justifyContent": "space-between",
                      "alignItems": "center", "marginBottom": "12px"}),
            html.Div(id="iv-modal-body"),
        ], id="iv-modal-content", style={}),
    ], id="iv-modal", style={"display": "none"}),

    html.Div([
        html.Div([
            html.Div([
                html.Span(id="save-modal-title",
                          style={"fontWeight": "700", "fontSize": "16px"}),
                html.Button("✕", id="close-save-btn", n_clicks=0,
                            style={"padding": "4px 10px", "borderRadius": "5px",
                                   "border": "1px solid #30363d", "background": "transparent",
                                   "color": "#e6edf3", "fontSize": "14px", "cursor": "pointer"}),
            ], style={"display": "flex", "justifyContent": "space-between",
                      "alignItems": "center", "marginBottom": "16px"}),
            html.Div(id="save-modal-body"),
        ], id="save-modal-content", style={}),
    ], id="save-modal", style={"display": "none"}),

    html.Div([
        html.Div([
            html.Div([
                html.Span(id="load-modal-title",
                          style={"fontWeight": "700", "fontSize": "16px"}),
                html.Button("✕", id="close-load-btn", n_clicks=0,
                            style={"padding": "4px 10px", "borderRadius": "5px",
                                   "border": "1px solid #30363d", "background": "transparent",
                                   "color": "#e6edf3", "fontSize": "14px", "cursor": "pointer"}),
            ], style={"display": "flex", "justifyContent": "space-between",
                      "alignItems": "center", "marginBottom": "16px"}),
            html.Div(id="load-modal-body"),
        ], id="load-modal-content", style={}),
    ], id="load-modal", style={"display": "none"}),

    dcc.Interval(id="tick", interval=30000, n_intervals=0),
    dcc.Interval(id="price-tick", interval=10000, n_intervals=0),
    dcc.Store(id="theme-store", data="dark"),
    dcc.Store(id="lang-store", data="el"),
    dcc.Store(id="symbol-store", data="BTC"),
    dcc.Store(id="expiry-store", data=None),
    dcc.Store(id="expiry-list", data=[]),
    dcc.Store(id="legs-store", data=[]),
    dcc.Store(id="rows-store", data=[]),
    dcc.Store(id="about-open", data=False),
    dcc.Store(id="analysis-open", data=False),
    dcc.Store(id="selected-strike-store", data=None),
    dcc.Store(id="strike-modal-open", data=False),
    dcc.Store(id="iv-modal-open", data=False),
    dcc.Store(id="saved-strategies", data=[]),
    dcc.Store(id="chart-modal-open", data=False),
    dcc.Store(id="chart-modal-strike", data=None),
    dcc.Store(id="save-modal-open", data=False),
    dcc.Store(id="load-modal-open", data=False),
], id="root", style={
    "minHeight": "100vh",
    "fontFamily": "Inter, -apple-system, Segoe UI, sans-serif",
    "background": THEMES["dark"]["bg"], "color": THEMES["dark"]["text"],
})


# ============================================================
# CALLBACKS
# ============================================================
COIN_ICONS = {"BTC": "₿", "ETH": "Ξ", "AAPL": "", "SPY": "📈", "TSLA": "🚗",
              "NVDA": "🎮", "MSFT": "🪟", "QQQ": "📊"}


@callback(
    Output("saved-strategies", "data", allow_duplicate=True),
    Input("tick", "n_intervals"),
    prevent_initial_call="initial_duplicate",
)
def init_saved_strategies(_n):
    """Load saved strategies from DB on app startup and every 30s."""
    try:
        data = strategies_db.load_strategies()
        if data:
            return data
        return no_update
    except Exception as e:
        print(f"[init_saved_strategies] error: {e}")
        return no_update

@callback(
    Output("live-price-display", "children"),
    Input("price-tick", "n_intervals"),
    Input("symbol-store", "data"),
)
def update_live_price(_, symbol):
    symbol = symbol or "BTC"
    icon = COIN_ICONS.get(symbol, "")
    if symbol in CRYPTO_SYMBOLS:
        price = get_crypto_spot(symbol)
    else:
        price = get_stock_spot(symbol)
    text = f"{symbol}: ${price:,.2f}" if price else f"{symbol}: —"
    return [
        html.Span(icon, className="coin-icon"),
        html.Span(text),
        html.Span(className="live-dot"),
    ]


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


@callback(Output("iv-modal-open", "data"),
          Input("iv-btn", "n_clicks"),
          Input("close-iv-btn", "n_clicks"),
          State("iv-modal-open", "data"), prevent_initial_call=True)
def toggle_iv_modal(n1, n2, current):
    return ctx.triggered_id == "iv-btn"


@callback(
    Output("strike-modal-open", "data"),
    Input("selected-strike-store", "data"),
    Input("close-strike-btn", "n_clicks"),
    prevent_initial_call=True,
)
def toggle_strike_modal(strike, n):
    if ctx.triggered_id == "close-strike-btn":
        return False
    if strike is not None:
        return True
    return False

@callback(
    Output("chart-modal-open", "data"),
    Output("chart-modal-strike", "data"),
    Input("show-chart-btn", "n_clicks"),
    Input("close-chart-btn", "n_clicks"),
    State("chain-grid", "selectedRows"),
    prevent_initial_call=True,
)
def toggle_chart_modal(n_show, n_close, selected):
    tid = ctx.triggered_id
    if tid == "close-chart-btn":
        return False, None
    if tid == "show-chart-btn" and selected:
        strike_val = selected[0].get("strike")
        if strike_val is not None:
            return True, strike_val
    return no_update, no_update
    

@callback(
    Output("chart-modal", "style"),
    Output("chart-modal-content", "style"),
    Output("chart-modal-title", "style"),
    Output("chart-modal-body", "children"),
    Input("chart-modal-open", "data"),
    Input("chart-modal-strike", "data"),
    Input("theme-store", "data"),
    Input("lang-store", "data"),
    State("symbol-store", "data"),
    State("rows-store", "data"),
)
def render_chart_modal(is_open, strike, theme, lang, symbol, rows):
    t = THEMES[theme]
    s = STRINGS[lang]

    if not is_open or strike is None:
        return {"display": "none"}, {}, {}, ""

    modal_style = {"display": "flex", "position": "fixed", "top": "0", "left": "0",
                   "width": "100%", "height": "100%",
                   "background": "rgba(0,0,0,0.85)",
                   "justifyContent": "center", "alignItems": "center",
                   "zIndex": "9999", "padding": "20px"}
    content_style = {"background": t["panel"], "border": f"1px solid {t['border']}",
                     "borderRadius": "12px", "padding": "24px",
                     "maxWidth": "900px", "width": "95%", "maxHeight": "90vh",
                     "overflowY": "auto", "color": t["text"]}
    title_style = {"fontWeight": "700", "fontSize": "18px", "color": STRIKE}

    symbol = symbol or "BTC"
    if symbol in CRYPTO_SYMBOLS:
        spot = get_crypto_spot(symbol) or 100
    else:
        spot = get_stock_spot(symbol) or 100

    target = None
    for r in (rows or []):
        if abs(r.get("strike", 0) - strike) < 0.01 and r["type"] == "call":
            target = r
            break
    if target is None:
        for r in (rows or []):
            if abs(r.get("strike", 0) - strike) < 0.01:
                target = r
                break

    if target is None:
        return modal_style, content_style, title_style, [html.Div("No data")]

    contract_size = CRYPTO_CONTRACT if symbol in CRYPTO_SYMBOLS else STOCK_CONTRACT
    fig = make_single_option_chart(
        spot, strike,
        target.get("premium") or target.get("bid") or 0,
        target["type"], symbol, contract_size,
    )

    body = [
        html.H3(f"{symbol} — Strike ${strike:,.0f}",
                style={"fontSize": "15px", "marginTop": "0", "color": STRIKE}),
        dcc.Graph(figure=fig, config={"displayModeBar": False},
                  style={"height": "500px"}),
    ]
    return modal_style, content_style, title_style, body

@callback(
    Output("selected-strike-store", "data", allow_duplicate=True),
    Input("analyze-strike-btn", "n_clicks"),
    State("chain-grid", "selectedRows"),
    prevent_initial_call=True,
)
def on_analyze_click(n, selected_rows):
    if not n or not selected_rows:
        return no_update
    row = selected_rows[0]
    strike_val = row.get("strike")
    if strike_val is None:
        return no_update
    return strike_val


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
    Output("iv-btn", "children"),
    Output("about-title", "children"),
    Output("strike-modal-title", "children"),
    Output("iv-modal-title", "children"),
    Output("save-strategy-btn", "children"),
    Output("load-strategy-btn", "children"),
    Output("save-modal-title", "children"),
    Output("load-modal-title", "children"),
    Input("lang-store", "data"),
)
def render_language(lang):
    s = STRINGS[lang]
    return (
        s["title"], s["subtitle"], s["symbol"], s["expiry"], s["presets"],
        s["presets_hint"], s["chain"], s["legs"], s["long"], s["short"],
        s["manual_hint"], s["underlying"], s["clear"],
        s["preset_cc"], s["preset_cs"], s["preset_ic"], s["preset_st"],
        s["about_btn"], s["analysis_btn"], s["iv_btn"],
        s["guide_title"], s["strike_modal_title"], s["iv_title"],
        s["sl_save_btn"], s["sl_load_btn"],
        s["sl_save_title"], s["sl_load_title"],
    )
    # ============================================================
# STRIKE MODAL RENDER
# ============================================================
@callback(
    Output("strike-modal", "style"),
    Output("strike-modal-content", "style"),
    Output("strike-modal-title", "style"),
    Output("strike-modal-body", "children"),
    Input("strike-modal-open", "data"),
    Input("selected-strike-store", "data"),
    Input("theme-store", "data"),
    Input("lang-store", "data"),
    Input("legs-store", "data"),
    State("symbol-store", "data"),
    State("rows-store", "data"),
)
def render_strike_modal(is_open, strike, theme, lang, legs, symbol, rows):
    t = THEMES[theme]
    s = STRINGS[lang]

    if not is_open or strike is None:
        return {"display": "none"}, {}, {}, ""

    modal_style = {"display": "flex", "position": "fixed", "top": "0", "left": "0",
                   "width": "100%", "height": "100%",
                   "background": "rgba(0,0,0,0.85)",
                   "justifyContent": "center", "alignItems": "center",
                   "zIndex": "9999", "padding": "20px"}
    content_style = {"background": t["panel"], "border": f"1px solid {t['border']}",
                     "borderRadius": "12px", "padding": "28px",
                     "maxWidth": "1300px", "width": "95%", "maxHeight": "92vh",
                     "overflowY": "auto", "color": t["text"]}
    title_style = {"fontWeight": "700", "fontSize": "20px", "color": STRIKE}

    symbol = symbol or "BTC"
    if symbol in CRYPTO_SYMBOLS:
        spot = get_crypto_spot(symbol) or 100
    else:
        spot = get_stock_spot(symbol) or 100

    call_r = None
    put_r = None
    for r in (rows or []):
        if abs(r.get("strike", 0) - strike) < 0.01:
            if r["type"] == "call":
                call_r = r
            elif r["type"] == "put":
                put_r = r

    is_crypto = symbol in CRYPTO_SYMBOLS
    contract_size = CRYPTO_CONTRACT if is_crypto else STOCK_CONTRACT

    call_an = _analyze_single_option(spot, strike, "call",
                                      (call_r or {}).get("premium", 0),
                                      (call_r or {}).get("iv", 0), is_crypto)
    put_an = _analyze_single_option(spot, strike, "put",
                                     (put_r or {}).get("premium", 0),
                                     (put_r or {}).get("iv", 0), is_crypto)

    def _moneyness_badge(an):
        mn = an["moneyness"]
        if mn == "itm":
            color, label = PROFIT, s["sm_moneyness_itm_short"]
        elif mn == "atm":
            color, label = WARN, s["sm_moneyness_atm_short"]
        else:
            color, label = LOSS, s["sm_moneyness_otm_short"]
        return html.Span(label, style={
            "background": f"{color}22", "color": color,
            "border": f"1px solid {color}66",
            "padding": "2px 10px", "borderRadius": "4px",
            "fontSize": "11px", "fontWeight": "700",
            "marginLeft": "8px",
        })

    what_is_call = s["sm_what_is_call"].format(
        sym=symbol, strike=f"{strike:,.0f}",
        breakeven=f"{call_an['breakeven']:,.2f}")
    what_is_put = s["sm_what_is_put"].format(
        sym=symbol, strike=f"{strike:,.0f}",
        breakeven=f"{put_an['breakeven']:,.2f}")

    section_what_is = html.Div([
        html.H3(s["sm_what_is"], style={"fontSize": "15px", "marginTop": "0",
                                         "color": STRIKE, "marginBottom": "12px"}),
        html.Div([
            html.Div([
                html.Span("🔵 CALL", style={"color": CALL_COLOR, "fontWeight": "700",
                                             "fontSize": "13px"}),
                _moneyness_badge(call_an),
                html.P(what_is_call, style={"fontSize": "13px", "margin": "8px 0 0 0",
                                             "lineHeight": "1.6", "color": t["text"]}),
            ], style={"flex": "1", "padding": "14px 16px",
                       "background": "rgba(46,204,113,0.06)",
                       "borderLeft": f"3px solid {CALL_COLOR}",
                       "borderRadius": "8px"}),
            html.Div([
                html.Span("🔴 PUT", style={"color": PUT_COLOR, "fontWeight": "700",
                                            "fontSize": "13px"}),
                _moneyness_badge(put_an),
                html.P(what_is_put, style={"fontSize": "13px", "margin": "8px 0 0 0",
                                            "lineHeight": "1.6", "color": t["text"]}),
            ], style={"flex": "1", "padding": "14px 16px",
                       "background": "rgba(231,76,60,0.06)",
                       "borderLeft": f"3px solid {PUT_COLOR}",
                       "borderRadius": "8px"}),
        ], style={"display": "flex", "gap": "16px", "marginBottom": "20px"}),
    ])

    def _status_row(label, value, color=None):
        return html.Tr([
            html.Td(label, style={"color": t["muted"], "padding": "6px 12px",
                                   "fontSize": "12px", "fontWeight": "600"}),
            html.Td(value, style={"color": color or t["text"], "padding": "6px 12px",
                                   "fontSize": "13px", "fontWeight": "700"}),
        ])

    def _status_block(an, opt_color, title):
        mn = an["moneyness"]
        mn_label = s[f"sm_moneyness_{mn}"]
        return html.Div([
            html.H4(title, style={"color": opt_color, "fontSize": "13px",
                                   "margin": "0 0 8px 0"}),
            html.Table([
                _status_row(s["sm_spot_now"], f"${spot:,.2f}", SPOT),
                _status_row(s["sm_moneyness"], mn_label,
                            PROFIT if mn == "itm" else (WARN if mn == "atm" else LOSS)),
                _status_row(s["sm_intrinsic"], f"${an['intrinsic']:,.2f}", t["text"]),
                _status_row(s["sm_time_value"], f"${an['time_value']:,.2f}", GREEK),
                _status_row(s["sm_breakeven_short"], f"${an['breakeven']:,.2f}", WARN),
                _status_row(s["capital_label"], f"${an['total_cost']:,.2f}", ACCENT),
            ], style={"width": "100%"}),
        ], style={"flex": "1", "padding": "14px 16px",
                   "background": t["panel_alt"], "borderRadius": "8px",
                   "border": f"1px solid {t['border']}"})

    section_status = html.Div([
        html.H3(s["sm_current_status"], style={"fontSize": "15px",
                                                "color": SPOT, "marginBottom": "12px"}),
        html.Div([
            _status_block(call_an, CALL_COLOR, "🔵 CALL"),
            _status_block(put_an, PUT_COLOR, "🔴 PUT"),
        ], style={"display": "flex", "gap": "16px", "marginBottom": "20px"}),
    ])

    def _th(label, tooltip, color):
        return html.Th([
            html.Span(label, style={"color": color}),
            html.Span(" ℹ️", title=tooltip, style={"cursor": "help",
                                                     "opacity": "0.5",
                                                     "fontSize": "10px"}),
        ], style={"padding": "10px", "textAlign": "left",
                   "borderBottom": f"2px solid {t['border']}",
                   "fontSize": "12px", "textTransform": "uppercase",
                   "letterSpacing": "0.5px"})

    def _row(label, tooltip, cv, pv, color_c=None, color_p=None):
        return html.Tr([
            html.Td([
                html.Span(label, style={"color": t["muted"], "fontWeight": "600"}),
                html.Span(" ℹ️", title=tooltip,
                          style={"cursor": "help", "opacity": "0.4",
                                 "fontSize": "10px", "marginLeft": "4px"}),
            ], style={"padding": "8px 10px", "borderBottom": f"1px solid {t['border']}"}),
            html.Td(cv, style={"color": color_c or t["text"], "fontWeight": "600",
                                "padding": "8px 10px",
                                "borderBottom": f"1px solid {t['border']}"}),
            html.Td(pv, style={"color": color_p or t["text"], "fontWeight": "600",
                                "padding": "8px 10px",
                                "borderBottom": f"1px solid {t['border']}"}),
        ])

    c_bid = f"${call_r['bid']:,.2f}" if call_r and call_r.get("bid") else "—"
    c_ask = f"${call_r['ask']:,.2f}" if call_r and call_r.get("ask") else "—"
    c_prem = f"${call_r['premium']:,.2f}" if call_r and call_r.get("premium") else "—"
    c_iv = f"{call_r['iv']:.1f}%" if call_r and call_r.get("iv") else "—"
    c_delta = f"{call_r['delta']:+.3f}" if call_r and call_r.get("delta") is not None else "—"
    c_prob = f"{call_r['prob_itm']*100:.1f}%" if call_r and call_r.get("prob_itm") is not None else "—"
    c_cap = f"${call_r['capital']:,.2f}" if call_r and call_r.get("capital") else "—"

    p_bid = f"${put_r['bid']:,.2f}" if put_r and put_r.get("bid") else "—"
    p_ask = f"${put_r['ask']:,.2f}" if put_r and put_r.get("ask") else "—"
    p_prem = f"${put_r['premium']:,.2f}" if put_r and put_r.get("premium") else "—"
    p_iv = f"{put_r['iv']:.1f}%" if put_r and put_r.get("iv") else "—"
    p_delta = f"{put_r['delta']:+.3f}" if put_r and put_r.get("delta") is not None else "—"
    p_prob = f"{put_r['prob_itm']*100:.1f}%" if put_r and put_r.get("prob_itm") is not None else "—"
    p_cap = f"${put_r['capital']:,.2f}" if put_r and put_r.get("capital") else "—"

    contract_label = s["sm_contract_crypto"].format(sym=symbol) if is_crypto else s["sm_contract_stock"]

    analytics_table = html.Table([
        html.Thead([
            html.Tr([
                _th(s["field"], "", t["muted"]),
                _th(s["call_label"], "", CALL_COLOR),
                _th(s["put_label"], "", PUT_COLOR),
            ])
        ]),
        html.Tbody([
            _row(s["strike_label"], s["sm_tooltip_strike"],
                 f"${strike:,.2f}", f"${strike:,.2f}", STRIKE, STRIKE),
            _row("Bid", s["sm_tooltip_bid"], c_bid, p_bid, PROFIT, PROFIT),
            _row("Ask", s["sm_tooltip_ask"], c_ask, p_ask, LOSS, LOSS),
            _row(s["premium_label"], s["sm_tooltip_premium"], c_prem, p_prem),
            _row("IV", s["sm_tooltip_iv"].format(sym=symbol), c_iv, p_iv),
            _row("Delta", s["sm_tooltip_delta"].format(sym=symbol),
                 c_delta, p_delta, GREEK, GREEK),
            _row(s["prob_itm_label"], s["sm_tooltip_prob"], c_prob, p_prob,
                 PROFIT, PUT_COLOR),
            _row(s["capital_label"], s["sm_tooltip_capital"].format(size=contract_label),
                 c_cap, p_cap, ACCENT, ACCENT),
        ])
    ], className="analytics-table")

    section_table = html.Div([
        html.H3(s["sm_table_title"], style={"fontSize": "15px",
                                             "color": STRIKE, "marginBottom": "12px"}),
        analytics_table,
        html.Div(f"ℹ️ {s['sm_contract_note'].format(size=contract_label)}",
                 style={"fontSize": "11px", "color": t["muted"],
                        "fontStyle": "italic", "marginTop": "8px"}),
    ], style={"marginBottom": "20px"})

    def _interpretation(an, opt_type, opt_label, opt_color):
        prob = 0
        if opt_type == "call" and call_r and call_r.get("prob_itm") is not None:
            prob = call_r["prob_itm"] * 100
        elif opt_type == "put" and put_r and put_r.get("prob_itm") is not None:
            prob = put_r["prob_itm"] * 100
        prem = (call_r or {}).get("premium", 0) if opt_type == "call" else (put_r or {}).get("premium", 0)
        prem = prem or 0

        if prob < 25:
            pricing = s["sm_interp_cheap"].format(prem=f"{prem:,.2f}", prob=f"{prob:.1f}")
        elif prob > 60:
            pricing = s["sm_interp_expensive"].format(prem=f"{prem:,.2f}", prob=f"{prob:.1f}")
        else:
            pricing = s["sm_interp_mid"].format(prem=f"{prem:,.2f}", prob=f"{prob:.1f}")

        return html.Div([
            html.H4(opt_label, style={"color": opt_color, "fontSize": "13px",
                                       "margin": "0 0 8px 0"}),
            html.P(pricing, style={"fontSize": "13px", "margin": "0 0 8px 0",
                                    "lineHeight": "1.5"}),
            html.P(s["sm_interp_bullish"].format(sym=symbol),
                   style={"fontSize": "12px", "margin": "4px 0",
                          "color": PROFIT}),
            html.P(s["sm_interp_bearish"].format(sym=symbol),
                   style={"fontSize": "12px", "margin": "4px 0",
                          "color": LOSS}),
            html.P(s["sm_interp_neutral"], style={"fontSize": "12px",
                                                    "margin": "4px 0",
                                                    "color": t["muted"]}),
        ], style={"flex": "1", "padding": "14px 16px",
                   "background": "rgba(243,156,18,0.06)",
                   "borderLeft": f"3px solid {WARN}",
                   "borderRadius": "8px"})

    section_interpret = html.Div([
        html.H3(s["sm_interp_title"], style={"fontSize": "15px",
                                              "color": WARN, "marginBottom": "12px"}),
        html.Div([
            _interpretation(call_an, "call", "🔵 CALL", CALL_COLOR),
            _interpretation(put_an, "put", "🔴 PUT", PUT_COLOR),
        ], style={"display": "flex", "gap": "16px", "marginBottom": "20px"}),
    ])

    def _example_block(an, opt_type, opt_color, opt_label):
        up = an["example_up"]; down = an["example_down"]
        up_color = PROFIT if up["pnl"] >= 0 else LOSS
        down_color = PROFIT if down["pnl"] >= 0 else LOSS
        up_result = s["sm_example_win"] if up["pnl"] >= 0 else s["sm_example_lose"]
        down_result = s["sm_example_win"] if down["pnl"] >= 0 else s["sm_example_lose"]

        def _ex_line(label, price, payoff, cost, pnl, pnl_color, result):
            return html.Div([
                html.Div(label.format(sym=symbol, price=f"{price:,.2f}"),
                         style={"fontSize": "12px", "color": t["muted"],
                                "marginBottom": "6px"}),
                html.Div([
                    html.Span(f"{s['sm_example_payoff']}: ", style={"color": t["muted"]}),
                    html.Span(f"${payoff:+,.2f}", style={"fontWeight": "600"}),
                    html.Span(f"  •  {s['sm_example_cost']}: ", style={"color": t["muted"],
                                                                          "marginLeft": "10px"}),
                    html.Span(f"${-cost:+,.2f}", style={"fontWeight": "600"}),
                ], style={"fontSize": "12px", "marginBottom": "4px"}),
                html.Div([
                    html.Span(f"{s['sm_example_result']}: ", style={"color": t["muted"]}),
                    html.Span(f"${pnl:+,.2f}", style={"fontWeight": "800",
                                                        "color": pnl_color,
                                                        "fontSize": "14px"}),
                    html.Span(f"  {result}", style={"color": pnl_color,
                                                      "fontWeight": "700",
                                                      "fontSize": "11px",
                                                      "marginLeft": "8px"}),
                ], style={"fontSize": "12px"}),
            ], style={"padding": "10px 12px", "background": t["panel"],
                       "borderRadius": "6px", "marginBottom": "8px",
                       "border": f"1px solid {t['border']}"})

        prem = an["total_cost"]
        up_payoff = up["pnl"] + prem
        down_payoff = down["pnl"] + prem

        return html.Div([
            html.H4(f"💡 {opt_label}", style={"color": opt_color,
                                                "fontSize": "13px",
                                                "margin": "0 0 8px 0"}),
            _ex_line(s["sm_example_up"], up["price"], up_payoff, prem,
                     up["pnl"], up_color, up_result),
            _ex_line(s["sm_example_down"], down["price"], down_payoff, prem,
                     down["pnl"], down_color, down_result),
        ], style={"flex": "1"})

    section_example = html.Div([
        html.H3(s["sm_example_title"], style={"fontSize": "15px",
                                                "color": ACCENT, "marginBottom": "12px"}),
        html.Div([
            _example_block(call_an, "call", CALL_COLOR, "CALL"),
            _example_block(put_an, "put", PUT_COLOR, "PUT"),
        ], style={"display": "flex", "gap": "16px", "marginBottom": "20px"}),
    ])

    def _make_chart(an, opt_type, opt_color, title):
        prem_usd = an["total_cost"] / an["contract_size"] if an["contract_size"] else 0
        fig = make_single_option_chart(spot, strike, prem_usd,
                                        opt_type, symbol, an["contract_size"])
        fig.add_vline(x=an["breakeven"], line_dash="dash", line_color=WARN,
                      line_width=1.5,
                      annotation_text=f"BE ${an['breakeven']:,.0f}",
                      annotation_position="top left",
                      annotation_font=dict(color=WARN, size=10))
        return fig

    call_chart = None
    if call_r:
        call_chart = dcc.Graph(
            figure=_make_chart(call_an, "call", CALL_COLOR, s["call_chart_title"]),
            config={"displayModeBar": False}, style={"height": "260px"})
    else:
        call_chart = html.Div("No call data", style={"padding": "40px", "color": t["muted"]})

    put_chart = None
    if put_r:
        put_chart = dcc.Graph(
            figure=_make_chart(put_an, "put", PUT_COLOR, s["put_chart_title"]),
            config={"displayModeBar": False}, style={"height": "260px"})
    else:
        put_chart = html.Div("No put data", style={"padding": "40px", "color": t["muted"]})

    charts_row = html.Div([
        html.Div([
            html.H4(s["call_chart_title"],
                    style={"color": CALL_COLOR, "fontSize": "13px", "margin": "0 0 8px 0"}),
            call_chart,
        ], style={"flex": "1"}),
        html.Div([
            html.H4(s["put_chart_title"],
                    style={"color": PUT_COLOR, "fontSize": "13px", "margin": "0 0 8px 0"}),
            put_chart,
        ], style={"flex": "1"}),
    ], style={"display": "flex", "gap": "16px", "marginBottom": "20px"})

    def _greek_row(name, value_c, value_p, desc):
        return html.Div([
            html.Div([
                html.Span(name, style={"fontWeight": "700", "color": GREEK,
                                        "fontSize": "13px"}),
                html.Span(f"  {desc}", style={"color": t["muted"],
                                                "fontSize": "11px"}),
            ], style={"marginBottom": "4px"}),
            html.Div([
                html.Span(f"🔵 CALL: {value_c}", style={"color": CALL_COLOR,
                                                          "fontWeight": "600",
                                                          "fontSize": "12px",
                                                          "marginRight": "20px"}),
                html.Span(f"🔴 PUT: {value_p}", style={"color": PUT_COLOR,
                                                         "fontWeight": "600",
                                                         "fontSize": "12px"}),
            ]),
        ], style={"padding": "8px 12px", "background": "rgba(155,89,182,0.06)",
                   "borderLeft": f"3px solid {GREEK}",
                   "borderRadius": "6px", "marginBottom": "6px"})

    section_greeks = html.Div([
        html.H3(s["sm_greeks_title"], style={"fontSize": "15px",
                                               "color": GREEK, "marginBottom": "12px"}),
        _greek_row("Delta", c_delta, p_delta, s["greek_delta_desc"]),
        _greek_row("Gamma",
                   f"{call_r['gamma']:+.6f}" if call_r and call_r.get("gamma") is not None else "—",
                   f"{put_r['gamma']:+.6f}" if put_r and put_r.get("gamma") is not None else "—",
                   s["greek_gamma_desc"]),
        _greek_row("Theta",
                   f"{call_r['theta']:+.4f}" if call_r and call_r.get("theta") is not None else "—",
                   f"{put_r['theta']:+.4f}" if put_r and put_r.get("theta") is not None else "—",
                   s["greek_theta_desc"]),
        _greek_row("Vega",
                   f"{call_r['vega']:+.4f}" if call_r and call_r.get("vega") is not None else "—",
                   f"{put_r['vega']:+.4f}" if put_r and put_r.get("vega") is not None else "—",
                   s["greek_vega_desc"]),
    ], style={"marginBottom": "20px"})

    def make_add_btn(label, sublabel, strike_val, opt_type, side, className, color):
        return html.Div([
            html.Button(
                label,
                id={"type": "add-btn", "strike": str(strike_val),
                    "opt": opt_type, "side": side},
                n_clicks=0,
                className=f"add-btn {className}",
                style={"width": "100%"},
            ),
            html.Div(sublabel, style={"fontSize": "11px", "color": color,
                                       "textAlign": "center",
                                       "marginTop": "4px",
                                       "opacity": "0.85"}),
        ], style={"display": "flex", "flexDirection": "column"})

    add_btns = html.Div([
        make_add_btn(s["add_call_long"],
                     s["sm_btn_explain_call_long"].format(sym=symbol,
                                                           be=f"{call_an['breakeven']:,.0f}"),
                     strike, "call", "long", "add-btn-long", PROFIT),
        make_add_btn(s["add_call_short"],
                     s["sm_btn_explain_call_short"].format(sym=symbol,
                                                            be=f"{call_an['breakeven']:,.0f}"),
                     strike, "call", "short", "add-btn-short", LOSS),
        make_add_btn(s["add_put_long"],
                     s["sm_btn_explain_put_long"].format(sym=symbol,
                                                          be=f"{put_an['breakeven']:,.0f}"),
                     strike, "put", "long", "add-btn-long", PROFIT),
        make_add_btn(s["add_put_short"],
                     s["sm_btn_explain_put_short"].format(sym=symbol,
                                                           be=f"{put_an['breakeven']:,.0f}"),
                     strike, "put", "short", "add-btn-short", LOSS),
    ], className="add-btn-grid")

    body = [
        section_what_is,
        section_status,
        section_table,
        section_interpret,
        section_example,
        charts_row,
        section_greeks,
        add_btns,
    ]
    return modal_style, content_style, title_style, body


# ============================================================
# IV MODAL RENDER
# ============================================================
@callback(
    Output("iv-modal", "style"),
    Output("iv-modal-content", "style"),
    Output("iv-modal-title", "style"),
    Output("iv-modal-body", "children"),
    Input("iv-modal-open", "data"),
    Input("theme-store", "data"),
    Input("lang-store", "data"),
    Input("rows-store", "data"),
    State("symbol-store", "data"),
)
def render_iv_modal(is_open, theme, lang, rows, symbol):
    t = THEMES[theme]
    s = STRINGS[lang]

    if not is_open:
        return {"display": "none"}, {}, {}, ""

    modal_style = {"display": "flex", "position": "fixed", "top": "0", "left": "0",
                   "width": "100%", "height": "100%",
                   "background": "rgba(0,0,0,0.8)",
                   "justifyContent": "center", "alignItems": "center",
                   "zIndex": "9999", "padding": "20px"}
    content_style = {"background": t["panel"], "border": f"1px solid {t['border']}",
                     "borderRadius": "12px", "padding": "24px",
                     "maxWidth": "1100px", "width": "95%", "maxHeight": "92vh",
                     "overflowY": "auto", "color": t["text"]}
    title_style = {"fontWeight": "700", "fontSize": "18px", "color": SPOT}

    symbol = symbol or "BTC"
    if symbol in CRYPTO_SYMBOLS:
        spot = get_crypto_spot(symbol) or 100
    else:
        spot = get_stock_spot(symbol) or 100

    if not rows:
        body = [html.Div(s["iv_no_data"],
                         style={"padding": "20px", "color": t["muted"],
                                "fontSize": "14px"})]
        return modal_style, content_style, title_style, body

    chart = dcc.Graph(
        figure=make_iv_chart(rows, spot, symbol, lang),
        config={"displayModeBar": False},
        style={"height": "420px"},
    )

    hint = html.Div(s["iv_hint"],
                    style={"marginTop": "16px",
                           "padding": "10px 14px",
                           "background": "rgba(88,166,255,0.08)",
                           "borderLeft": "3px solid #58a6ff",
                           "borderRadius": "6px",
                           "color": t["muted"],
                           "fontSize": "12px"})

    body = [
        html.H3(f"{s['iv_title']} — {symbol}",
                style={"fontSize": "15px", "marginTop": "0", "color": SPOT}),
        chart,
        hint,
    ]
    return modal_style, content_style, title_style, body


# ============================================================
# ADD BUTTONS from strike modal
# ============================================================
@callback(
    Output("legs-store", "data", allow_duplicate=True),
    Input({"type": "add-btn", "strike": dash_all, "opt": dash_all, "side": dash_all}, "n_clicks"),
    State("legs-store", "data"),
    State("rows-store", "data"),
    prevent_initial_call=True,
)
def add_from_modal(n, legs, rows):
    if not n or not ctx.triggered_id:
        return no_update
    strike_val = float(ctx.triggered_id["strike"])
    opt = ctx.triggered_id["opt"]
    side = ctx.triggered_id["side"]
    side_val = 1 if side == "long" else -1

    for r in (rows or []):
        if abs(r.get("strike", 0) - strike_val) < 0.01 and r["type"] == opt:
            leg = {"side": side_val, "type": opt, "strike": strike_val,
                   "premium": r.get("bid") or 0, "instrument": r["instrument"]}
            return (legs or []) + [leg]
    return no_update


# ============================================================
# ABOUT MODAL
# ============================================================
@callback(Output("about-modal", "style"), Output("about-content", "style"),
          Output("about-title", "style"), Output("about-body", "children"),
          Input("about-open", "data"), Input("theme-store", "data"), Input("lang-store", "data"))
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
        body = """### 🛡️ Covered Call\nΑγοράζεις 0.1 BTC, πουλάς OTM call.\n\n### ↗️ Call Spread\nLong call + short πιο ψηλό call.\n\n### 🦅 Iron Condor\n4 legs.\n\n### ⚖️ Straddle\nLong call + long put.\n\n### 🔍 Analyze Button\nΠάτα το 🔍 δίπλα σε κάθε strike για λεπτομέρειες.\n\n### 📈 IV Button\nΠάτα το 📈 για να δεις το Volatility Smile.\n\n### 💾 Save / 📂 Strategies\nΑποθήκευσε και φόρτωσε τις στρατηγικές σου."""
    else:
        body = """### 🛡️ Covered Call\nBuy 0.1 BTC, sell OTM call.\n\n### ↗️ Call Spread\nLong call + short higher call.\n\n### 🦅 Iron Condor\n4 legs.\n\n### ⚖️ Straddle\nLong call + long put.\n\n### 🔍 Analyze Button\nPress 🔍 next to any strike for details.\n\n### 📈 IV Button\nPress 📈 to see the Volatility Smile.\n\n### 💾 Save / 📂 Strategies\nSave and load your strategies."""
    return modal_style, content_style, title_style, body


# ============================================================
# ANALYSIS MODAL
# ============================================================
@callback(
    Output("analysis-modal", "style"), Output("analysis-content", "style"),
    Output("analysis-title", "style"), Output("analysis-body", "children"),
    Input("analysis-open", "data"), Input("legs-store", "data"),
    Input("theme-store", "data"), Input("lang-store", "data"),
    State("symbol-store", "data"), State("chain-grid", "rowData"))
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
                html.Div(s["analysis_no_legs"], style={"padding": "20px", "fontSize": "14px", "color": t["muted"]}))
    symbol = symbol or "BTC"
    spot = get_crypto_spot(symbol) if symbol in CRYPTO_SYMBOLS else get_stock_spot(symbol)
    if spot is None:
        spot = 100
    analysis = analyze_strategy(spot, legs, symbol, lang, chain_rows)
    if not analysis:
        return (modal_style, content_style, title_style, html.Div("Error", style={"padding": "20px"}))
    body = []
    if analysis["outcomes"]:
        body.append(html.H3(s["outcomes_title"], style={"fontSize": "15px", "marginTop": "0"}))
        ors = []
        for o in analysis["outcomes"]:
            pc = PROFIT if o["pnl_usd"] >= 0 else LOSS
            pt = f"({o['prob']*100:.0f}%)" if o.get("prob") is not None else ""
            ors.append(html.Div([
                html.Span(o["label"], className="outcome-label", style={"fontWeight": "600", "color": t["text"]}),
                html.Span(f"${o['pnl_usd']:+,.2f} ({o['pnl_pct']:+.2f}%)", className="outcome-pnl", style={"color": pc}),
                html.Span(pt, className="outcome-prob"),
            ], className="outcome-row"))
        body.append(html.Div(ors, style={"background": t["panel_alt"], "borderRadius": "8px", "overflow": "hidden", "marginBottom": "16px"}))
    if analysis["even_vs"]:
        body.append(html.H3(s["even_title"], style={"fontSize": "15px"}))
        evs = []
        if "usd" in analysis["even_vs"]:
            v = analysis["even_vs"]["usd"]; pct = (v / spot - 1) * 100
            evs.append(html.Div([html.Span(f"{s['even_vs_usd']}: ", style={"color": t["muted"]}),
                                 html.Span(f"${v:,.2f}", style={"fontWeight": "700", "color": WARN}),
                                 html.Span(f" ({pct:+.1f}%)", style={"color": t["muted"], "fontSize": "12px", "marginLeft": "6px"})], style={"padding": "6px 0"}))
        if "crypto" in analysis["even_vs"]:
            v = analysis["even_vs"]["crypto"]
            lbl = s["even_vs_crypto"] if analysis["is_crypto"] else s["even_vs_stock"]
            pct = (v / spot - 1) * 100
            evs.append(html.Div([html.Span(f"{lbl}: ", style={"color": t["muted"]}),
                                 html.Span(f"${v:,.2f}", style={"fontWeight": "700", "color": WARN}),
                                 html.Span(f" ({pct:+.1f}%)", style={"color": t["muted"], "fontSize": "12px", "marginLeft": "6px"})], style={"padding": "6px 0"}))
        body.append(html.Div(evs, style={"background": t["panel_alt"], "padding": "12px 16px", "borderRadius": "8px", "marginBottom": "16px"}))
    if analysis["warnings"]:
        for w in analysis["warnings"]:
            body.append(html.Div(w["text"], className="warn-card"))
    body.append(html.H3(s["analysis_your_legs"], style={"fontSize": "15px"}))
    items = []
    for i, leg in enumerate(legs):
        sc = PROFIT if leg["side"] > 0 else RED
        st = "LONG" if leg["side"] > 0 else "SHORT"
        d = (f"{leg['instrument']} @ ${spot:,.2f}" if leg["type"] == "underlying"
             else f"{leg['type'].upper()} K=${leg['strike']:,.0f} @ ${leg['premium']:,.2f}")
        items.append(html.Div([html.Span(f"#{i+1} ", style={"color": t["muted"], "fontSize": "11px"}),
                               html.Span(f"{st} ", style={"color": sc, "fontWeight": "700", "fontSize": "13px"}),
                               html.Span(d, style={"color": t["text"], "fontSize": "13px"})],
                              style={"padding": "4px 0", "borderBottom": f"1px solid {t['border']}"}))
    body.append(html.Div(items, style={"marginBottom": "16px"}))
    body.append(html.H3(s["exec_title"], style={"fontSize": "15px"}))
    ers = []
    for step in analysis["exec_steps"]:
        cls = "exec-buy" if step["action"] == "BUY" else "exec-sell"
        ers.append(html.Div([html.Span(step["action"], className=f"exec-action {cls}"),
                             html.Span(step["desc"], style={"color": t["text"], "fontSize": "13px"}),
                             html.Span(f"  (${step['cost']:+,.2f})", style={"color": PROFIT if step["cost"] < 0 else LOSS, "fontWeight": "600", "marginLeft": "6px"})],
                            style={"marginBottom": "6px"}))
    cap = f"${analysis['capital_usd']:,.2f}"
    if analysis["is_crypto"] and analysis["capital_crypto"] > 0:
        cap += f" ({analysis['capital_crypto']:.3f} BTC)"
    body.append(html.Div([html.Div(ers),
                          html.Div([html.Span(s["exec_capital"] + ": ", style={"fontWeight": "600", "fontSize": "13px"}),
                                    html.Span(cap, style={"color": ACCENT, "fontWeight": "700", "fontSize": "15px"})],
                                   style={"marginTop": "12px", "paddingTop": "10px", "borderTop": f"1px dashed {t['border']}"}),
                          html.Div(s["one_contract_crypto" if analysis["is_crypto"] else "one_contract_stock"],
                                   style={"fontSize": "11px", "color": t["muted"], "fontStyle": "italic", "marginTop": "4px"})],
                         className="exec-card"))
    body.append(html.H3(s["analysis_summary"], style={"fontSize": "15px"}))
    nc = analysis["net_cost"]; cc = RED if nc > 0 else PROFIT
    body.append(html.Div([
        html.Div([html.Span(s["analysis_net_cost"] + ": ", style={"fontWeight": "600"}),
                  html.Span(f"${nc:,.2f}" if abs(nc) >= 0.01 else "$0", style={"color": cc, "fontWeight": "700"})], style={"marginBottom": "6px"}),
        html.Div([html.Span(s["analysis_max_profit"] + ": ", style={"fontWeight": "600"}),
                  html.Span(f"${analysis['max_profit']:,.2f}", style={"color": PROFIT, "fontWeight": "700"})], style={"marginBottom": "6px"}),
        html.Div([html.Span(s["analysis_max_loss"] + ": ", style={"fontWeight": "600"}),
                  html.Span(f"${analysis['max_loss']:,.2f}", style={"color": LOSS, "fontWeight": "700"})], style={"marginBottom": "6px"}),
    ], style={"background": t["panel_alt"], "padding": "12px 16px", "borderRadius": "8px", "marginBottom": "16px"}))
    body.append(html.H3(s["analysis_chart"], style={"fontSize": "15px"}))
    body.append(dcc.Graph(figure=analysis["chart"], config={"displayModeBar": False},
                          style={"marginBottom": "16px", "height": "320px"}))
    return modal_style, content_style, title_style, body


# ============================================================
# SAVE / LOAD STRATEGIES
# ============================================================
@callback(
    Output("save-modal-open", "data"),
    Output("load-modal-open", "data"),
    Input("save-strategy-btn", "n_clicks"),
    Input("load-strategy-btn", "n_clicks"),
    Input("close-save-btn", "n_clicks"),
    Input("close-load-btn", "n_clicks"),
    prevent_initial_call=True,
)
def toggle_sl_modals(n1, n2, n3, n4):
    tid = ctx.triggered_id
    if tid == "save-strategy-btn":
        return True, False
    if tid == "load-strategy-btn":
        return False, True
    return False, False


@callback(
    Output("save-modal", "style"),
    Output("save-modal-content", "style"),
    Output("save-modal-title", "style"),
    Output("save-modal-body", "children"),
    Input("save-modal-open", "data"),
    Input("theme-store", "data"),
    Input("lang-store", "data"),
    Input("legs-store", "data"),
    State("symbol-store", "data"),
)
def render_save_modal(is_open, theme, lang, legs, symbol):
    t = THEMES[theme]
    s = STRINGS[lang]

    if not is_open:
        return {"display": "none"}, {}, {}, ""

    modal_style = {"display": "flex", "position": "fixed", "top": "0", "left": "0",
                   "width": "100%", "height": "100%",
                   "background": "rgba(0,0,0,0.8)",
                   "justifyContent": "center", "alignItems": "center",
                   "zIndex": "9999", "padding": "20px"}
    content_style = {"background": t["panel"], "border": f"1px solid {t['border']}",
                     "borderRadius": "12px", "padding": "24px",
                     "maxWidth": "480px", "width": "95%",
                     "color": t["text"]}
    title_style = {"fontWeight": "700", "fontSize": "16px", "color": PROFIT}

    symbol = symbol or "BTC"

    if not legs:
        body = [html.Div(s["sl_save_empty"],
                          style={"padding": "12px 0", "color": t["muted"],
                                 "fontSize": "13px"})]
        return modal_style, content_style, title_style, body

    legs_summary = html.Div([
        html.Div([
            html.Span(f"#{i+1} ", style={"color": t["muted"], "fontSize": "11px"}),
            html.Span("LONG " if leg["side"] > 0 else "SHORT ",
                      style={"color": PROFIT if leg["side"] > 0 else LOSS,
                             "fontWeight": "700", "fontSize": "12px"}),
            html.Span(
                f"{leg['instrument']} (spot)" if leg["type"] == "underlying"
                else f"{leg['type'].upper()} K=${leg['strike']:,.0f} @ ${leg['premium']:,.2f}",
                style={"color": t["text"], "fontSize": "12px"}),
        ], style={"padding": "3px 0", "borderBottom": f"1px solid {t['border']}"})
        for i, leg in enumerate(legs)
    ], style={"marginBottom": "16px", "maxHeight": "150px", "overflowY": "auto",
              "padding": "10px 12px", "background": t["panel_alt"],
              "borderRadius": "6px"})

    body = [
        html.Div([
            html.Label(s["sl_save_name"],
                       style={"fontSize": "12px", "fontWeight": "600",
                              "color": t["muted"], "marginBottom": "6px",
                              "display": "block"}),
            dcc.Input(
                id="save-name-input",
                type="text",
                placeholder=s["sl_save_placeholder"],
                style={
                    "width": "100%", "padding": "10px 14px",
                    "borderRadius": "8px", "border": f"1px solid {t['border']}",
                    "background": t["panel_alt"], "color": t["text"],
                    "fontSize": "13px", "fontFamily": "Inter, sans-serif",
                    "outline": "none",
                },
            ),
        ], style={"marginBottom": "16px"}),
        html.Div([
            html.Div("🎯 LEGS:", style={"fontSize": "11px", "fontWeight": "700",
                                          "color": t["muted"], "marginBottom": "8px",
                                          "letterSpacing": "0.08em"}),
            legs_summary,
        ]),
        html.Div([
            html.Button(s["sl_save_confirm"], id="save-confirm-btn", n_clicks=0,
                        style={"flex": "1", "padding": "11px 16px",
                               "borderRadius": "8px", "border": "none",
                               "background": f"linear-gradient(135deg, {PROFIT} 0%, #27ae60 100%)",
                               "color": "#ffffff", "fontWeight": "700",
                               "fontSize": "13px", "cursor": "pointer",
                               "fontFamily": "Inter, sans-serif"}),
            html.Button(s["sl_save_cancel"], id="save-cancel-btn", n_clicks=0,
                        style={"flex": "1", "padding": "11px 16px",
                               "borderRadius": "8px",
                               "border": f"1px solid {t['border']}",
                               "background": "transparent", "color": t["text"],
                               "fontWeight": "600", "fontSize": "13px",
                               "cursor": "pointer",
                               "fontFamily": "Inter, sans-serif"}),
        ], style={"display": "flex", "gap": "10px", "marginTop": "16px"}),
        html.Div(id="save-feedback",
                 style={"marginTop": "12px", "fontSize": "12px",
                        "textAlign": "center"}),
    ]
    return modal_style, content_style, title_style, body


@callback(
    Output("saved-strategies", "data", allow_duplicate=True),
    Output("save-feedback", "children"),
    Output("save-modal-open", "data", allow_duplicate=True),
    Input("save-confirm-btn", "n_clicks"),
    Input("save-cancel-btn", "n_clicks"),
    State("save-name-input", "value"),
    State("legs-store", "data"),
    State("symbol-store", "data"),
    State("saved-strategies", "data"),
    State("lang-store", "data"),
    prevent_initial_call=True,
)
def save_strategy(n_confirm, n_cancel, name, legs, symbol, saved, lang):
    tid = ctx.triggered_id
    if tid == "save-cancel-btn":
        return no_update, "", False
    if tid != "save-confirm-btn":
        return no_update, "", no_update
    s = STRINGS[lang]
    if not legs:
        return no_update, s["sl_save_empty"], no_update
    if not name or not name.strip():
        return no_update, s["sl_save_no_name"], no_update

    # Save to Postgres
    new_id = strategies_db.save_strategy(name.strip(), symbol or "BTC", legs)
    if new_id is None:
        return no_update, "❌ DB error", no_update

    # Build the new entry directly (don't re-query — avoids race conditions)
    new_entry = {
        "id": str(new_id),
        "name": name.strip(),
        "symbol": symbol or "BTC",
        "legs": legs,
        "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    current = list(saved) if saved else []
    current = [e for e in current if e.get("id") != str(new_id)]
    updated = [new_entry] + current
    return updated, s["sl_saved"], False


@callback(
    Output("load-modal", "style"),
    Output("load-modal-content", "style"),
    Output("load-modal-title", "style"),
    Output("load-modal-body", "children"),
    Input("load-modal-open", "data"),
    Input("theme-store", "data"),
    Input("lang-store", "data"),
    Input("saved-strategies", "data"),
)
def render_load_modal(is_open, theme, lang, saved):
    t = THEMES[theme]
    s = STRINGS[lang]

    if not is_open:
        return {"display": "none"}, {}, {}, ""

    modal_style = {"display": "flex", "position": "fixed", "top": "0", "left": "0",
                   "width": "100%", "height": "100%",
                   "background": "rgba(0,0,0,0.8)",
                   "justifyContent": "center", "alignItems": "center",
                   "zIndex": "9999", "padding": "20px"}
    content_style = {"background": t["panel"], "border": f"1px solid {t['border']}",
                     "borderRadius": "12px", "padding": "24px",
                     "maxWidth": "560px", "width": "95%", "maxHeight": "85vh",
                     "overflowY": "auto", "color": t["text"]}
    title_style = {"fontWeight": "700", "fontSize": "16px", "color": GREEK}

    if not saved:
        body = [html.Div(s["sl_load_empty"],
                          style={"padding": "20px 0", "color": t["muted"],
                                 "fontSize": "13px", "textAlign": "center"})]
        return modal_style, content_style, title_style, body

    items = []
    for entry in saved:
        legs_count = len(entry.get("legs", []))
        items.append(html.Div([
            html.Div([
                html.Div([
                    html.Span(entry["name"],
                              style={"fontWeight": "700", "fontSize": "14px",
                                     "color": t["text"]}),
                    html.Span(f"  ·  {entry.get('symbol', '')}",
                              style={"color": ACCENT, "fontWeight": "600",
                                     "fontSize": "12px"}),
                ]),
                html.Div([
                    html.Span(f"{legs_count} {s['sl_legs_count']}",
                              style={"color": t["muted"], "fontSize": "11px"}),
                    html.Span(f"  ·  {s['sl_saved_at']}: {entry.get('saved_at', '')}",
                              style={"color": t["muted"], "fontSize": "11px",
                                     "marginLeft": "6px"}),
                ], style={"marginTop": "2px"}),
            ], style={"flex": "1"}),
            html.Div([
                html.Button(s["sl_load_btn_action"],
                            id={"type": "load-strategy-item", "id": entry["id"]},
                            n_clicks=0,
                            style={"padding": "7px 14px", "borderRadius": "6px",
                                   "border": "none",
                                   "background": f"linear-gradient(135deg, {ACCENT} 0%, #4a8fe7 100%)",
                                   "color": "#fff", "fontWeight": "700",
                                   "fontSize": "11px", "cursor": "pointer",
                                   "marginRight": "6px",
                                   "fontFamily": "Inter, sans-serif"}),
                html.Button(s["sl_delete_btn_action"],
                            id={"type": "delete-strategy-item", "id": entry["id"]},
                            n_clicks=0,
                            style={"padding": "7px 14px", "borderRadius": "6px",
                                   "border": f"1px solid {RED}44",
                                   "background": f"{RED}22", "color": RED,
                                   "fontWeight": "700", "fontSize": "11px",
                                   "cursor": "pointer",
                                   "fontFamily": "Inter, sans-serif"}),
            ], style={"display": "flex", "alignItems": "center"}),
        ], style={"display": "flex", "alignItems": "center",
                   "padding": "12px 14px", "borderRadius": "8px",
                   "background": t["panel_alt"], "marginBottom": "8px",
                   "border": f"1px solid {t['border']}"}))

    body = [
        html.Div(s["sl_load_hint"], style={"fontSize": "12px",
                                            "color": t["muted"],
                                            "marginBottom": "12px"}),
        html.Div(items),
    ]
    return modal_style, content_style, title_style, body


@callback(
    Output("legs-store", "data", allow_duplicate=True),
    Output("symbol-store", "data", allow_duplicate=True),
    Output("load-modal-open", "data", allow_duplicate=True),
    Input({"type": "load-strategy-item", "id": dash_all}, "n_clicks"),
    prevent_initial_call=True,
)
def load_strategy(n):
    if not ctx.triggered_id or isinstance(ctx.triggered_id, str):
        return no_update, no_update, no_update

    # If max clicks across all load buttons is 0, nobody clicked → skip
    triggered_clicks = max(n) if isinstance(n, list) and n else (n or 0)
    if triggered_clicks == 0:
        return no_update, no_update, no_update

    target_id = ctx.triggered_id.get("id")
    if not target_id:
        return no_update, no_update, no_update
    
    all_strats = strategies_db.load_strategies()
    for entry in all_strats:
        if entry["id"] == target_id:
            return entry["legs"], entry.get("symbol", "BTC"), False
    return no_update, no_update, no_update


@callback(
    Output("saved-strategies", "data", allow_duplicate=True),
    Input({"type": "delete-strategy-item", "id": dash_all}, "n_clicks"),
    prevent_initial_call=True,
)
def delete_strategy(n):
    # Only delete if the triggered button was ACTUALLY clicked (n_clicks > 0)
    if not ctx.triggered_id or isinstance(ctx.triggered_id, str):
        return no_update
    # Get the actual n_clicks value for the triggered button
    triggered_clicks = 0
    if isinstance(n, list):
        # find the n_clicks of the triggered button
        try:
            # n is a list of all values; ctx.triggered_prop_ids has the ID
            for tid, prop in ctx.triggered_prop_ids.items():
                # tid is a string representation; we need to extract value
                pass
        except Exception:
            pass
        triggered_clicks = max(n) if n else 0
    else:
        triggered_clicks = n or 0

    # If max clicks across all buttons is 0, nobody clicked → skip
    if triggered_clicks == 0:
        return no_update

    target_id = ctx.triggered_id.get("id")
    if not target_id:
        return no_update
    
    strategies_db.delete_strategy(target_id)
    return strategies_db.load_strategies()


# ============================================================
# SYMBOLS / EXPIRIES
# ============================================================
@callback(Output("symbol-buttons", "children"),
          Input("symbol-store", "data"), Input("theme-store", "data"))
def render_symbol_buttons(active, theme):
    t = THEMES[theme]
    buttons = []
    for sym in ALL_SYMBOLS:
        is_active = (sym == active)
        icon = COIN_ICONS.get(sym, "")
        label = f"{icon} {sym}" if icon else sym
        if is_active:
            style = {"background": f"linear-gradient(135deg, {ACCENT} 0%, #4a8fe7 100%)",
                     "color": "#ffffff", "border": f"1px solid {ACCENT}",
                     "boxShadow": f"0 4px 14px {ACCENT}66", "fontWeight": "700"}
        else:
            style = {"background": t["btn_bg"], "color": t["text"], "border": f"1px solid {t['border']}"}
        buttons.append(html.Button(label, id={"type": "symbol-btn", "value": sym},
                                   n_clicks=0, className="ds-symbol", style=style))
    return buttons


@callback(Output("symbol-store", "data", allow_duplicate=True),
          Input({"type": "symbol-btn", "value": dash_all}, "n_clicks"),
          prevent_initial_call=True)
def on_symbol_click(_):
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
            data = [[ts, label] for ts, label in expiries[:24]]
            default = expiries[0][1] if expiries else None
        else:
            expiries = get_stock_expiries(symbol)
            data = [[label, label] for ts, label in expiries[:24]]
            default = expiries[0][1] if expiries else None
    except Exception:
        return [], None
    return data, default


@callback(Output("expiry-buttons", "children"),
          Input("expiry-list", "data"), Input("expiry-store", "data"),
          Input("theme-store", "data"))
def render_expiry_buttons(expiry_list, active, theme):
    t = THEMES[theme]
    if not expiry_list:
        return html.Span("Loading…", style={"fontSize": "12px", "color": t["muted"]})
    buttons = []
    for ts, label in expiry_list:
        is_active = (str(label) == str(active))
        style = ({"background": f"linear-gradient(135deg, {ACCENT} 0%, #4a8fe7 100%)",
                  "color": "#ffffff", "border": f"1px solid {ACCENT}",
                  "boxShadow": f"0 3px 10px {ACCENT}55", "fontWeight": "700"}
                 if is_active else
                 {"background": t["btn_bg"], "color": t["text"], "border": f"1px solid {t['border']}"})
        buttons.append(html.Button(label, id={"type": "expiry-btn", "value": str(label)},
                                   n_clicks=0, className="ds-expiry", style=style))
    return buttons


@callback(Output("expiry-store", "data", allow_duplicate=True),
          Input({"type": "expiry-btn", "value": dash_all}, "n_clicks"),
          prevent_initial_call=True)
def on_expiry_click(_):
    return ctx.triggered_id["value"] if ctx.triggered_id else no_update


@callback(Output("rows-store", "data"),
          Input("tick", "n_intervals"), Input("symbol-store", "data"),
          Input("expiry-store", "data"), State("expiry-list", "data"),
          prevent_initial_call=True)
def fetch_rows(_, symbol, expiry, expiry_list):
    if not symbol or not expiry or not expiry_list:
        return []
    valid_labels = {str(label) for _, label in expiry_list}
    if str(expiry) not in valid_labels:
        return []
    try:
        if symbol in CRYPTO_SYMBOLS:
            return get_crypto_chain(symbol, expiry, 200)
        else:
            return get_stock_chain(symbol, expiry, 200)
    except Exception as e:
        print(f"[fetch] error: {e}")
        return []


@callback(Output("chain-grid", "rowData"),
          Output("row-count", "children"),
          Output("chain-grid", "selectedRows", allow_duplicate=True),
          Input("rows-store", "data"), Input("lang-store", "data"),
          State("symbol-store", "data"),
          prevent_initial_call='initial_duplicate')
def apply_chain_view(rows, lang, symbol):
    s = STRINGS[lang]
    if not rows:
        return [], f"0 {s['contracts']}", no_update

    symbol = symbol or "BTC"
    spot = get_crypto_spot(symbol) if symbol in CRYPTO_SYMBOLS else get_stock_spot(symbol)
    if spot is None:
        spot = rows[0]["strike"] if rows else 0

    chain = build_chain_view(rows, spot=spot)
    selected = [chain[0]] if chain else []
    return chain, f"{len(chain)} strikes", selected

@callback(
    Output("chain-grid", "columnDefs"),
    Input("symbol-store", "data"),
    prevent_initial_call=False,
)
def update_grid_columns(_symbol):
    full_columns = [
        {"field": "c_bid", "headerName": "C Bid", "minWidth": 70, "flex": 1},
        {"field": "c_ask", "headerName": "C Ask", "minWidth": 70, "flex": 1},
        {"field": "c_iv", "headerName": "C IV", "minWidth": 60, "flex": 1},
        {"field": "c_delta", "headerName": "C Δ", "minWidth": 60, "flex": 1},
        {"field": "strike", "headerName": "STRIKE", "minWidth": 100, "flex": 1.2},
        {"field": "volume", "headerName": "VOL", "minWidth": 70, "flex": 1,
         "headerTooltip": "Volume — πόσα contracts αγοράστηκαν σήμερα"},
        {"field": "oi", "headerName": "OI", "minWidth": 70, "flex": 1,
         "headerTooltip": "Open Interest — πόσα contracts είναι ανοιχτά"},
        {"field": "p_delta", "headerName": "P Δ", "minWidth": 60, "flex": 1},
        {"field": "p_iv", "headerName": "P IV", "minWidth": 60, "flex": 1},
        {"field": "p_ask", "headerName": "P Ask", "minWidth": 70, "flex": 1},
        {"field": "p_bid", "headerName": "P Bid", "minWidth": 70, "flex": 1},
    ]
    return full_columns

    


# ============================================================
# MANUAL ADD LONG / SHORT / UNDERLYING
# ============================================================
@callback(Output("legs-store", "data", allow_duplicate=True),
          Input("add-long-btn", "n_clicks"),
          State("chain-grid", "selectedRows"), State("legs-store", "data"),
          State("rows-store", "data"), prevent_initial_call=True)
def add_long(n, selected, legs, rows):
    if not selected or n == 0 or not rows:
        return legs
    row = selected[0]; k = row["strike"]
    for r in rows:
        if r["type"] == "call" and abs(r["strike"] - k) < 0.01:
            return (legs or []) + [{"side": 1, "type": "call", "strike": k,
                                    "premium": r.get("bid") or 0, "instrument": r["instrument"]}]
    return legs


@callback(Output("legs-store", "data", allow_duplicate=True),
          Input("add-short-btn", "n_clicks"),
          State("chain-grid", "selectedRows"), State("legs-store", "data"),
          State("rows-store", "data"), prevent_initial_call=True)
def add_short(n, selected, legs, rows):
    if not selected or n == 0 or not rows:
        return legs
    row = selected[0]; k = row["strike"]
    for r in rows:
        if r["type"] == "call" and abs(r["strike"] - k) < 0.01:
            return (legs or []) + [{"side": -1, "type": "call", "strike": k,
                                    "premium": r.get("bid") or 0, "instrument": r["instrument"]}]
    return legs


@callback(Output("legs-store", "data", allow_duplicate=True),
          Input("add-underlying-btn", "n_clicks"),
          State("symbol-store", "data"), State("legs-store", "data"),
          prevent_initial_call=True)
def add_underlying(n, symbol, legs):
    if n == 0:
        return legs
    return (legs or []) + [{"side": 1, "type": "underlying", "strike": 0,
                            "premium": 0, "instrument": symbol}]


@callback(Output("legs-store", "data", allow_duplicate=True),
          Input("clear-legs-btn", "n_clicks"), prevent_initial_call=True)
def clear_legs(n):
    return [] if n else no_update


# ============================================================
# PRESETS
# ============================================================
@callback(Output("legs-store", "data", allow_duplicate=True),
          Input("preset-cc", "n_clicks"),
          State("symbol-store", "data"), State("rows-store", "data"),
          prevent_initial_call=True)
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
    return [{"side": 1, "type": "underlying", "strike": 0, "premium": 0, "instrument": symbol},
            {"side": -1, "type": "call", "strike": call["strike"],
             "premium": call.get("bid") or 0, "instrument": call["instrument"]}]


@callback(Output("legs-store", "data", allow_duplicate=True),
          Input("preset-cs", "n_clicks"),
          State("symbol-store", "data"), State("rows-store", "data"),
          prevent_initial_call=True)
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
    return [{"side": 1, "type": "call", "strike": l["strike"],
             "premium": l.get("ask") or l.get("bid") or 0, "instrument": l["instrument"]},
            {"side": -1, "type": "call", "strike": s["strike"],
             "premium": s.get("bid") or 0, "instrument": s["instrument"]}]


@callback(Output("legs-store", "data", allow_duplicate=True),
          Input("preset-ic", "n_clicks"),
          State("symbol-store", "data"), State("rows-store", "data"),
          prevent_initial_call=True)
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
    return [{"side": 1, "type": "put", "strike": op[0]["strike"],
             "premium": op[0].get("ask") or 0, "instrument": op[0]["instrument"]},
            {"side": -1, "type": "put", "strike": op[1]["strike"],
             "premium": op[1].get("bid") or 0, "instrument": op[1]["instrument"]},
            {"side": -1, "type": "call", "strike": oc[0]["strike"],
             "premium": oc[0].get("bid") or 0, "instrument": oc[0]["instrument"]},
            {"side": 1, "type": "call", "strike": oc[1]["strike"],
             "premium": oc[1].get("ask") or 0, "instrument": oc[1]["instrument"]}]


@callback(Output("legs-store", "data", allow_duplicate=True),
          Input("preset-st", "n_clicks"),
          State("symbol-store", "data"), State("rows-store", "data"),
          prevent_initial_call=True)
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
    return [{"side": 1, "type": "call", "strike": c["strike"],
             "premium": c.get("ask") or 0, "instrument": c["instrument"]},
            {"side": 1, "type": "put", "strike": p["strike"],
             "premium": p.get("ask") or 0, "instrument": p["instrument"]}]


# ============================================================
# LEGS RENDER
# ============================================================
@callback(Output("legs-list", "children"),
          Input("legs-store", "data"), Input("theme-store", "data"), Input("lang-store", "data"))
def render_legs(legs, theme, lang):
    t = THEMES[theme]; s = STRINGS[lang]
    if not legs:
        return html.Span(s["no_legs"], style={"fontSize": "12px", "color": t["muted"]})
    items = []
    for i, leg in enumerate(legs):
        color = PROFIT if leg["side"] > 0 else RED
        st = "LONG" if leg["side"] > 0 else "SHORT"
        d = (f"{leg['instrument']} (spot)" if leg["type"] == "underlying"
             else f"{leg['type'].upper()} K={leg['strike']} @ ${round(leg['premium'], 2)}")
        items.append(html.Div([html.Span(f"#{i+1} ", style={"color": t["muted"], "fontSize": "11px"}),
                               html.Span(f"{st} ", style={"color": color, "fontWeight": "700", "fontSize": "12px"}),
                               html.Span(d, style={"color": t["text"], "fontSize": "12px"})],
                              style={"padding": "3px 0", "borderBottom": f"1px solid {t['border']}"}))
    return items


# ============================================================
# MAIN CHART
# ============================================================
@callback(Output("chart", "figure"),
          Input("legs-store", "data"),
          Input("chain-grid", "selectedRows"),
          Input("rows-store", "data"),
          State("symbol-store", "data"),
          State("theme-store", "data"),
          prevent_initial_call=False)
def update_chart(legs, selected_rows, rows, symbol, theme):
    symbol = symbol or "BTC"
    theme = theme or "dark"
    spot = get_crypto_spot(symbol) if symbol in CRYPTO_SYMBOLS else get_stock_spot(symbol)
    if spot is None:
        spot = 100

    if legs:
        return make_multi_leg_chart(spot, legs, symbol, theme)

    if not rows:
        t = THEMES[theme]
        fig = go.Figure()
        fig.update_layout(paper_bgcolor=t["chart_bg"], plot_bgcolor=t["chart_bg"],
                          font=dict(color=t["text"]),
                          annotations=[dict(text="Loading...",
                                            x=0.5, y=0.5, xref="paper", yref="paper",
                                            showarrow=False,
                                            font=dict(color=t["muted"], size=14))])
        return fig

    if selected_rows:
        strike = selected_rows[0].get("strike")
    else:
        all_strikes = sorted(set(r["strike"] for r in rows))
        if all_strikes:
            strike = min(all_strikes, key=lambda k: abs(k - spot))
        else:
            strike = None

    if strike is None:
        return go.Figure()

    target = None
    for r in rows:
        if abs(r.get("strike", 0) - strike) < 0.01 and r["type"] == "call":
            target = r
            break
    if target is None:
        for r in rows:
            if abs(r.get("strike", 0) - strike) < 0.01:
                target = r
                break

    if target is None:
        return go.Figure()

    contract_size = CRYPTO_CONTRACT if symbol in CRYPTO_SYMBOLS else STOCK_CONTRACT
    return make_single_option_chart(
        spot,
        strike,
        target.get("premium") or target.get("bid") or 0,
        target["type"],
        symbol,
        contract_size,
    )


# ============================================================
# THEME APPLY
# ============================================================
@callback(Output("root", "style"), Output("header", "style"),
          Output("symbol-row", "style"), Output("expiry-row", "style"),
          Output("preset-row", "style"), Output("grid-panel", "style"),
          Output("grid-header", "style"), Output("manual-row", "style"),
          Output("legs-panel", "style"),
          Output("main-grid", "style"), Output("chain-grid", "className"),
          Output("theme-toggle", "style"), Output("theme-toggle", "children"),
          Output("lang-toggle", "style"), Output("about-btn", "style"),
          Output("analysis-btn", "style"), Output("live-price-display", "style"),
          Input("theme-store", "data"), prevent_initial_call=False)
def apply_theme(theme):
    t = THEMES[theme]
    root_style = {"minHeight": "100vh",
                  "fontFamily": "Inter, -apple-system, Segoe UI, sans-serif",
                  "background": t["bg"], "color": t["text"]}
    header_style = {"display": "flex", "alignItems": "center",
                    "padding": "14px 28px", "background": t["panel"],
                    "borderBottom": f"1px solid {t['border']}", "gap": "16px",
                    "backdropFilter": "blur(8px)",
                    "position": "sticky", "top": "0", "zIndex": "100"}
    row_style = {"display": "flex", "alignItems": "center",
                 "padding": "12px 24px 0 24px", "flexWrap": "wrap",
                 "background": t["bg"], "color": t["text"]}
    expiry_style = {"display": "flex", "alignItems": "center",
                    "padding": "12px 24px", "flexWrap": "wrap",
                    "background": t["bg"], "color": t["text"]}
    preset_style = {"display": "flex", "alignItems": "center",
                    "padding": "0 24px 12px 24px", "flexWrap": "wrap",
                    "background": t["bg"], "color": t["text"]}
    panel_style = {"borderRadius": "10px", "overflow": "hidden",
                   "background": t["panel"], "border": f"1px solid {t['border']}",
                   "boxShadow": "0 1px 3px rgba(0,0,0,0.15), 0 8px 24px rgba(0,0,0,0.08)"}
    grid_header_style = {"padding": "12px 16px", "background": t["panel"],
                         "borderBottom": f"1px solid {t['border']}"}
    manual_row_style = {"padding": "0 16px 12px 16px", "borderBottom": f"1px solid {t['border']}"}
    legs_panel_style = {"padding": "12px 16px", "minHeight": "100px",
                        "maxHeight": "180px", "overflowY": "auto",
                        "borderTop": f"1px solid {t['border']}"}
    main_grid_style = {"display": "grid", "gridTemplateColumns": "1fr",
                       "gap": "16px", "padding": "20px 28px"}
    button_style = {"fontSize": "15px", "padding": "8px 12px",
                    "borderRadius": "8px", "cursor": "pointer",
                    "border": f"1px solid {t['border']}",
                    "background": t["panel"], "color": t["text"],
                    "fontWeight": "600"}
    btn_style = {"marginLeft": "12px", "background": t["btn_bg"], "color": t["text"],
                 "border": f"1px solid {t['border']}", "padding": "9px 14px",
                 "borderRadius": "8px", "fontSize": "12px", "fontWeight": "600",
                 "cursor": "pointer"}
    analysis_btn_style = {"marginLeft": "8px", "background": t["btn_bg"],
                          "color": t["text"], "border": f"1px solid {t['border']}",
                          "padding": "9px 14px", "borderRadius": "8px",
                          "fontSize": "12px", "fontWeight": "600", "cursor": "pointer"}
    live_price_style = {"fontSize": "20px", "fontWeight": "700", "color": PROFIT,
                        "fontFamily": "'JetBrains Mono', monospace",
                        "letterSpacing": "-0.02em",
                        "padding": "7px 16px 7px 14px",
                        "background": "rgba(46, 204, 113, 0.08)",
                        "borderRadius": "10px", "border": "1px solid rgba(46, 204, 113, 0.25)",
                        "display": "inline-flex", "alignItems": "center", "gap": "10px"}
    grid_class = t["grid_theme"]
    icon = "☀️" if theme == "dark" else "🌙"
    return (root_style, header_style, row_style, expiry_style, preset_style,
            panel_style, grid_header_style, manual_row_style, legs_panel_style,
            main_grid_style, grid_class, button_style, icon,
            button_style, btn_style, analysis_btn_style, live_price_style)


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8051))
    app.run(debug=False, host="0.0.0.0", port=port)
