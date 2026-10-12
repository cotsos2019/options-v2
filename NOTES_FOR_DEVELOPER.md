# Notes for AI / Developer

## Project: Options Dashboard v2

### Τι είναι
Dash web app για options data — crypto (Deribit, live) + stocks (yfinance, delayed). Chain view grid, multi-leg strategy builder, Greeks, chain analytics, bilingual (EL/EN), dark/light theme.

### URLs
- Live: https://options-v2.onrender.com
- Local: http://127.0.0.1:8051
- GitHub: https://github.com/user5461/options-v2

### Φάκελος
C:\Users\Administrator\projects\options-v2

---

## Tech Stack
- Python 3.12.3
- Dash 4.x
- dash-ag-grid 35.x
- Plotly 7.x
- requests + urllib3
- yfinance + curl_cffi
- gunicorn

## requirements.txt
dash
plotly
dash-ag-grid
requests
urllib3
yfinance
curl_cffi
gunicorn

---

## Δομή αρχείων
options-v2/
- app.py                    # ΟΛΟΣ ο κώδικας (single-file)
- requirements.txt
- Procfile                  # "web: gunicorn app:server"
- runtime.txt               # "python-3.12.3"
- .gitignore
- NOTES_FOR_DEVELOPER.md
- START_HERE.md
- app_v2_stage21_backup.py  # backup πριν από chain view
- .venv/

---

## Contract Sizes (ΣΗΜΑΝΤΙΚΟ)
- Crypto (BTC, ETH): 1 option contract = 0.1 BTC/ETH
- Stocks (AAPL, SPY, TSLA, NVDA, MSFT, QQQ): 1 option contract = 100 shares

Χρησιμοποιείται σε όλους τους υπολογισμούς (Capital, Payoff, Greeks).

---

## Data Sources

### Crypto — Deribit
Base: https://www.deribit.com/api/v2

Endpoints:
- /public/get_instruments?currency=BTC&kind=option&expired=false — λίστα με expirations
- /public/get_book_summary_by_currency?currency=BTC&kind=option — bulk tickers
- /public/get_index_price?index_name=btc_usd — spot price

ΚΡΙΣΙΜΟ:
- Τα bid_price/ask_price από book summary είναι σε BTC — πολλαπλασιάζονται με spot για USD.
- Instrument name: BTC-10OCT26-75000-C — expiry label = parts[1].
- Το book summary ΔΕΝ έχει expiration_timestamp — φιλτράρουμε με string match (-10OCT26-).
- ΔΕΝ δίνει Greeks — υπολογίζονται με Black-Scholes από το IV.

### Stocks — yfinance
ΚΡΙΣΙΜΟ: Windows SSL error → shared session με curl_cffi:
_stock_session = curl_requests.Session(impersonate="chrome")
_stock_session.verify = False
Δημιουργείται μία φορά. ΜΗΝ κάνεις νέο session κάθε φορά (rate limit).

- Expiry format: 2026-10-16 (ISO).
- ΔΕΝ δίνει Greeks — υπολογίζονται με Black-Scholes από το IV.

---

## Architecture

### Stores (Dash state)
- symbol-store — "BTC" / "ETH" / "AAPL" / "SPY" / "TSLA" / "NVDA" / "MSFT" / "QQQ"
- expiry-store — ενεργό expiry label
- expiry-list — όλα τα expiries (max 12)
- legs-store — legs στρατηγικής
- rows-store — raw options (πριν το chain view grouping)
- theme-store — "dark" / "light"
- lang-store — "el" / "en"
- about-open, analysis-open, strike-modal-open — booleans
- selected-strike-store — για το modal του strike

### Leg format
{"side": 1, "type": "call", "strike": 75000, "premium": 1234.56, "instrument": "BTC-10OCT26-75000-C"}

### Raw row format (rows-store)
{"instrument": "...", "type": "call", "strike": 75000, "bid": X, "ask": Y, "premium": Z,
 "capital": W, "prob_itm": P, "iv": V, "delta": D, "gamma": G, "theta": T, "vega": E,
 "iv_value": iv_dec, "volume": N, "oi": M}

### Chain view row format (chain-grid.rowData)
{"strike": 75000,
 "c_bid": ..., "c_ask": ..., "c_iv": ..., "c_delta": ..., "c_instrument": ...,
 "p_bid": ..., "p_ask": ..., "p_iv": ..., "p_delta": ..., "p_instrument": ...}

### Chain view grouping
build_chain_view(rows) — ομαδοποιεί rows ανά strike, βάζει call αριστερά, put δεξιά.

### Cache
In-memory dict _cache:
- Crypto expiries: 600s
- Crypto chain: 60s
- Crypto spot: 30s
- Stock expiries: 3600s
- Stock chain: 120s
- Stock spot: 60s

Στο Render καθαρίζεται σε κάθε restart.

### Black-Scholes
Χρησιμοποιείται για:
- Greeks (delta, gamma, theta, vega)
- Prob ITM (N(d2) για calls, N(-d2) για puts)

r = 0.045. T υπολογίζεται από expiry label (crypto: 10OCT26, stocks: 2026-10-16).

---

## Features (Stage 22A)

### Grid — Chain View
- Strike στη μέση (χρυσό, bold, underlined)
- Calls αριστερά (C Bid, C Ask, C IV, C Δ)
- Puts δεξιά (P Δ, P IV, P Ask, P Bid)
- Bid = πράσινο, Ask = κόκκινο
- Headers: Calls πράσινα, Puts κόκκινα, Strike χρυσό
- Sorting: built-in AG Grid (1x asc, 2x desc, 3x clear)

### Live Price
- Κέντρο header, πράσινο
- Coin logo μπροστά (₿ για BTC, Ξ για ETH, 📈 για SPY, κλπ.)
- Ανανεώνεται κάθε 10 δευτερόλεπτα

### Presets (auto από spot)
- 🛡️ Covered Call — Long 0.1 BTC + Short OTM call
- ↗️ Call Spread — Long call + Short higher call
- 🦅 Iron Condor — 4 legs γύρω από spot
- ⚖️ Straddle — Long call + Long put στο spot

### Manual
- + LONG / + SHORT — χρησιμοποιεί το call της επιλεγμένης γραμμής
- + Underlying — long το υποκείμενο

### Analysis Modal (📊)
- 📊 Αποτελέσματα στη Λήξη (2-3 σενάρια ανά preset)
- 📍 Σημεία Ισορροπίας (Even vs full USD/BTC)
- ⚠️ Προειδοποιήσεις
- 🎯 Legs
- 📐 Greeks (συνολικά)
- ⚙️ Εντολές Εκτέλεσης
- 💰 Σύνοψη (max profit, max loss, net cost)
- 📈 Chart payoff
- 🎲 Όλα τα Σενάρια (6)

### About Modal (❓)
Γενικές εξηγήσεις στρατηγικών + Greeks + contract sizes.

### Theme
- Dark (default) / Light
- Χρώματα:
  - BG: #0e1117
  - Panel: #161b22
  - Border: #30363d
  - Text: #e6edf3
  - Calls/Profit: #2ecc71
  - Puts/Loss: #e74c3c
  - Strike: #f39c12
  - Spot: #58a6ff
  - Accent: #1f6feb
  - Greeks: #9b59b6

### Language
- Ελληνικά (default) / Αγγλικά
- Όλα τα labels αλλάζουν μέσω lang-store

### Layout
- Header: title (left) + live price (center) + buttons (right)
- Grid: 63% πλάτος (1.9fr)
- Chart: 37% πλάτος (1.1fr)
- Responsive: stacked < 1200px

---

## Γνωστά Gotchas

1. Dash "Duplicate Output" → allow_duplicate=True
2. Αριθμός outputs = return values
3. ALL as dash_all στην αρχή
4. Deribit prices σε BTC → ×spot για USD
5. yfinance shared session
6. Δύο expiry formats: 10OCT26 (crypto), 2026-10-16 (stocks)
7. Contract sizes: crypto=0.1, stocks=100
8. Render sleep: 30-60s wake up
9. Local port 8051, Render: PORT env var
10. Browser cache μετά από deploy: Ctrl+F5 (όχι μόνο Ctrl+Shift+R)
11. AG Grid cellRenderer: ΔΕΝ δουλεύει με {"function": "..."} για DOM elements. Warning #101.

---

## Ιστορικό Stages

- 1-7: BTC → ETH → Stocks → Multi-leg → Presets → Deploy
- 8-9: Filters + Crypto prices σε USD
- 10-11: Volume, νέα symbols, Light mode, όμορφα buttons
- 12-14: 12 expiries, bilingual, preset guide, Analysis modal
- 15-17A: Hints, Capital, Prob ITM, Execution, Warnings
- 18: Wider grid (63%)
- 19: Greeks (Delta, Gamma, Theta, Vega)
- 20: 0.1 BTC contract + Options-Lab presentation
- 21: Live price in header + Outcomes για όλα τα presets
- 22A: Chain view grid + coin logos + sorting (ΤΡΕΧΟΥΣΑ)
- 22B (σε εξέλιξη): 🔍 Analyze button — το cellRenderer απέτυχε

---

## Τι ΔΕΝ δουλεύει (για 22B)

- Το κουμπί 🔍 μέσα στο Strike cell απέτυχε (AG Grid warning #101).
- Λύση: κουμπί 🔍 Analyze πάνω από το grid δίπλα στα LONG/SHORT.
- Λογική: πατάς γραμμή → πατάς Analyze → modal με το strike.

---

## Επόμενα βήματα

1. Fix 22B: 🔍 Analyze button πάνω από το grid
2. Ίσως: IV chart (volatility smile)
3. Ίσως: Save/load strategies
4. Ίσως: Mobile βελτιώσεις

---

## Πώς να τρέξεις τοπικά
cd C:\Users\Administrator\projects\options-v2
.venv\Scripts\Activate.ps1
python app.py
http://127.0.0.1:8051

## Πώς να κάνεις deploy
git add .
git commit -m "description"
git push
Render auto-deploys σε 2-3 λεπτά

## Rollback
git log --oneline
git checkout <hash>

---

## Τελευταία κατάσταση
- ✅ Chain view grid (Strike κέντρο, Calls αριστερά, Puts δεξιά)
- ✅ Live price με coin logos
- ✅ Sorting σε όλες τις στήλες
- ✅ Bid πράσινο / Ask κόκκινο / Strike χρυσό
- ✅ BTC, ETH, AAPL, SPY, TSLA, NVDA, MSFT, QQQ
- ✅ 12 expiries
- ✅ Multi-leg + presets
- ✅ Greeks, Capital, Prob ITM
- ✅ Execution Instructions + Warnings + Outcomes
- ✅ Bilingual (EL/EN)
- ✅ Dark/Light
- ✅ Deployed στο Render
- ⏳ Σε εξέλιξη: 🔍 Analyze button (22B)