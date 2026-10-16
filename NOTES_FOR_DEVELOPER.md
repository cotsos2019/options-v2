# Notes for AI / Developer

## Project: Options Dashboard v2

### Τι είναι
Dash web app για options data — crypto (Deribit, live) + stocks (yfinance, delayed). Chain view grid, multi-leg strategy builder, Greeks, educational Analyze modal, Volatility Smile, Save/Load strategies με Postgres, bilingual (EL/EN), dark/light theme, professional UI.

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
- PostgreSQL (local: options_db) + psycopg2-binary
- python-dotenv
- gunicorn

## requirements.txt
dash
plotly
dash-ag-grid
requests
urllib3
yfinance
curl_cffi
psycopg2-binary
python-dotenv
gunicorn

---

## Δομή αρχείων

options-v2/
- app.py                      # ΟΛΟΣ ο κώδικας (single-file)
- db.py                       # Postgres helpers
- .env                        # DB credentials (ΔΕΝ ανεβαίνει στο Git)
- requirements.txt
- Procfile                    # "web: gunicorn app:server"
- runtime.txt                 # "python-3.12.3"
- .gitignore
- NOTES_FOR_DEVELOPER.md
- START_HERE.md
- README.md
- app_v2_stage21_backup.py    # backup πριν από chain view
- .venv/

---

## Contract Sizes (ΣΗΜΑΝΤΙΚΟ)

Crypto (BTC, ETH): 1 option contract = 0.1 BTC/ETH
Stocks (AAPL, SPY, TSLA, NVDA, MSFT, QQQ): 1 option contract = 100 shares

Χρησιμοποιείται σε όλους τους υπολογισμούς (Capital, Payoff, Greeks).

Παράδειγμα: Premium = $3,212.78 (ανά BTC) → total cost = $3,212.78 × 0.1 = $321.28.

---

## Data Sources

### Crypto — Deribit
Base: https://www.deribit.com/api/v2

Endpoints:
- /public/get_instruments?currency=BTC&kind=option&expired=false — λίστα με expirations
- /public/get_book_summary_by_currency?currency=BTC&kind=option — bulk tickers (1 request, γρήγορο)
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

## Database (Postgres)

### Σύνδεση
Credentials στο `.env` (ΔΕΝ ανεβαίνει στο Git):

DB_HOST=localhost
DB_PORT=5432
DB_NAME=options_db
DB_USER=postgres
DB_PASSWORD=***

### Πίνακας strategies

CREATE TABLE strategies (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(200) NOT NULL,
    symbol      VARCHAR(20) NOT NULL,
    legs        JSONB NOT NULL,
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW()
);

### db.py functions
- init_db() — δημιουργεί table αν δεν υπάρχει
- save_strategy(name, symbol, legs) → επιστρέφει id ή None
- load_strategies() → επιστρέφει list από dicts (newest first)
- delete_strategy(strategy_id) → True/False
- count_strategies() → int

### Πώς να δεις τη βάση

psql -U postgres -d options_db
SELECT id, name, symbol, created_at FROM strategies;
\q

---

## Architecture

### Stores (Dash state)

| Store | Περιεχόμενο |
|---|---|
| symbol-store | "BTC" / "ETH" / "AAPL" / "SPY" / "TSLA" / "NVDA" / "MSFT" / "QQQ" |
| expiry-store | Ενεργό expiry label |
| expiry-list | Όλα τα expiries (max 12) |
| legs-store | Legs στρατηγικής |
| rows-store | Raw options (πριν το chain view grouping) |
| theme-store | "dark" / "light" |
| lang-store | "el" / "en" |
| about-open | Boolean |
| analysis-open | Boolean |
| strike-modal-open | Boolean |
| selected-strike-store | Για το modal του strike |
| iv-modal-open | Boolean (για IV chart modal) |
| saved-strategies | Λίστα στρατηγικών (in-memory, γεμίζει από DB) |
| save-modal-open | Boolean |
| load-modal-open | Boolean |

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

| Τύπος | TTL |
|---|---|
| Crypto expiries | 600s |
| Crypto chain | 60s |
| Crypto spot | 30s |
| Stock expiries | 3600s |
| Stock chain | 120s |
| Stock spot | 60s |

Στο Render καθαρίζεται σε κάθε restart.

### Black-Scholes

Χρησιμοποιείται για:
- Greeks (delta, gamma, theta, vega)
- Prob ITM (N(d2) για calls, N(-d2) για puts)

r = 0.045. T υπολογίζεται από expiry label (crypto: 10OCT26, stocks: 2026-10-16).

---

## Features (Stage 28 — COMPLETE)

### Grid — Chain View

- Strike στη μέση (χρυσό, bold)
- Calls αριστερά (C Bid, C Ask, C IV, C Δ)
- Puts δεξιά (P Δ, P IV, P Ask, P Bid)
- Headers: Calls πράσινα, Puts κόκκινα, Strike χρυσό
- Row selection με click (χωρίς checkboxes)
- Highlight στη selected row
- Mono font για νούμερα (JetBrains Mono)
- Sorting: built-in AG Grid (1x asc, 2x desc, 3x clear)

### Live Price

- Κέντρο header, πράσινο
- Coin logo μπροστά (₿ για BTC, Ξ για ETH, 📈 για SPY, κλπ.)
- Pulsing dot (live indicator)
- Ανανεώνεται κάθε 10 δευτερόλεπτα

### Presets (auto από spot)

- Covered Call — Long 0.1 BTC + Short OTM call
- Call Spread — Long call + Short higher call
- Iron Condor — 4 legs γύρω από spot
- Straddle — Long call + Long put στο spot

ΣΗΜΑΝΤΙΚΟ: Τα presets δεν χρησιμοποιούν τη γραμμή που διάλεξες. Χτίζονται αυτόματα με βάση το spot.

### Manual

- + LONG / + SHORT — χρησιμοποιεί το call της επιλεγμένης γραμμής
- + Underlying — long το υποκείμενο

### Educational Analyze Modal (Stage 24)

Περιέχει:
- 📖 Τι είναι αυτό το option; — CALL & PUT explanation + moneyness badge (ITM/OTM/ATM)
- 📍 Τρέχουσα κατάσταση — Spot, moneyness, intrinsic, time value, break-even, capital
- 📊 Πίνακας δεδομένων — Bid, Ask, Premium, IV, Delta, Prob ITM, Capital με tooltips (ℹ️)
- 💡 Τι σημαίνει για μένα; — interpretation + προτάσεις
- 🎯 Παράδειγμα — πραγματικά σενάρια (up/down)
- 📈 Charts — CALL & PUT payoff με break-even γραμμή
- 📐 Greeks — Delta, Gamma, Theta, Vega με explanations
- 4 κουμπιά — ΑΓΟΡΑ/ΠΟΥΛΑ CALL/PUT με εξήγηση από κάτω

### Analysis Modal

- Αποτελέσματα στη Λήξη
- Σημεία Ισορροπίας
- Προειδοποιήσεις
- Legs
- Εντολές Εκτέλεσης
- Σύνοψη (max profit, max loss, net cost)
- Chart payoff
- Όλα τα Σενάρια (6)

### IV Chart Modal (Volatility Smile)

- IV ανά strike
- Spot γραμμή
- Bilingual hints

### Save / Load Strategies

- Save: γράφει στη Postgres
- Load: διαβάζει από Postgres
- Delete: διαγράφει από Postgres
- LocalStorage ΔΕΝ χρησιμοποιείται πια
- Auto-init στην εκκίνηση μέσω callback init_saved_strategies

### About Modal

Γενικές εξηγήσεις στρατηγικών + Greeks + contract sizes.

### Theme

Dark (default) / Light

Χρώματα:

| Χρήση | Κωδικός |
|---|---|
| BG | #0e1117 |
| Panel | #161b22 |
| Border | #30363d |
| Text | #e6edf3 |
| Calls/Profit | #2ecc71 |
| Puts/Loss | #e74c3c |
| Strike | #f39c12 |
| Spot | #58a6ff |
| Accent | #1f6feb |
| Greeks | #9b59b6 |
| Warning | #f39c12 |

### Language

Ελληνικά (default) / Αγγλικά — όλα τα labels αλλάζουν μέσω lang-store.

### Fonts

- Inter — UI text
- JetBrains Mono — νούμερα, grid cells

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
5. yfinance shared session με curl_cffi, verify=False
6. Δύο expiry formats: 10OCT26 (crypto), 2026-10-16 (stocks)
7. Contract sizes: crypto=0.1, stocks=100
8. Render sleep: 30-60s wake up
9. Local port 8051, Render: PORT env var
10. Browser cache μετά deploy: Ctrl+F5 (όχι μόνο Ctrl+Shift+R)
11. AG Grid: ΟΧΙ {"function": "..."} σε valueFormatter/cellStyle — σκάει το AG Grid 35.x με XSS warning
12. Pattern-matching IDs: ΠΡΕΠΕΙ να είναι strings (όχι numbers)
13. AG Grid rowSelection: {"mode": "singleRow", "checkboxes": False, "enableClickSelection": True} — αλλιώς θέλει κλικ στο checkbox
14. Pattern-matching callbacks με dash_all: Το callback ΠΥΡΟΔΟΤΕΙΤΑΙ ΑΥΤΟΜΑΤΑ όταν δημιουργούνται νέα components (π.χ. νέα delete buttons) → ΕΛΕΓΧΕ πάντα max(n) if isinstance(n, list) else n και if triggered_clicks == 0: return no_update
15. Postgres race condition: Το render_load_modal ΔΕΝ πρέπει να καλεί load_strategies() — χρησιμοποίησε το store

---

## Ιστορικό Stages

| Stage | Τι κάναμε |
|---|---|
| 1-7 | BTC → ETH → Stocks → Multi-leg → Presets → Deploy |
| 8-9 | Filters + Crypto prices σε USD |
| 10-11 | Volume, νέα symbols, Light mode, όμορφα buttons |
| 12-14 | 12 expiries, bilingual, preset guide, Analysis modal |
| 15-17A | Hints, Capital, Prob ITM, Execution, Warnings |
| 18 | Wider grid (63%), narrower chart (37%) |
| 19 | Greeks (Delta, Gamma, Theta, Vega) |
| 20 | 0.1 BTC contract size + Options-Lab presentation |
| 21 | Live price in header + Outcomes για όλα τα presets |
| 22A | Chain view grid + coin logos + sorting |
| 22B | Analyze button + Modal |
| 23 | IV Chart (Volatility Smile) |
| 24 | Educational Analyze Modal |
| 25 | Professional UI (Inter + JetBrains Mono, pulsing dot) |
| 26 | Save/Load strategies (localStorage αρχικά) |
| 27 | Fixed AG Grid XSS warnings + grid improvements |
| 28 | Postgres persistence + fix race condition σε delete/load + row selection click-anywhere |
| 29 | VOL + OI στήλες + 30 strikes + bigger grid + chart modal button |

---

## Τι ΔΕΝ δουλεύει / εκκρεμότητες

- cellRenderer για μπάρες VOL/OI — αφαιρέθηκε λόγω AG Grid 35.x XSS protection.
- cellClicked event — δεν πυροδοτείται. Λύση: κουμπί "📊 Chart" στο μενού.
- cellRenderer στο Strike column — αφαιρέθηκε λόγω AG Grid warning #101.

## Γνωστά Gotchas (update)

16. **VOL/OI στήλες**: numbers only. Τα `cellRenderer` με JS function ΔΕΝ δουλεύουν στο AG Grid 35.x (XSS protection).
17. **Chart button**: `show-chart-btn` χρησιμοποιεί `selectedRows` + `n_clicks` (όχι `cellClicked` που δεν πυροδοτείται).

---

## Επόμενα βήματα (candidates)

1. Deploy στο Render με Postgres (Neon ή Render Postgres)
2. Volume στήλη στο chain view
3. Greeks chart (visualization)
4. Περισσότερα symbols (AMZN, GOOGL, META, COIN, AMD, PLTR)
5. Export/Import στρατηγικών (JSON)
6. Watchlist (αγαπημένα symbols)
7. Multi-user με authentication
8. Alerts (ειδοποιήσεις όταν spot περάσει strike)

---

## Πώς να τρέξεις τοπικά

cd C:\Users\Administrator\projects\options-v2
.venv\Scripts\Activate.ps1
python app.py
http://127.0.0.1:8051

### Πρώτη φορά setup

python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Φτιάξε .env με τα DB credentials
python -c "import db; db.init_db()"

## Πώς να κάνεις deploy

git add .
git commit -m "description"
git push
Render auto-deploys σε 2-3 λεπτά

## Rollback

git log --oneline
git checkout <hash>

---

## Τελευταία κατάσταση (checkpoint)

- Chain view grid (Strike κέντρο, Calls αριστερά, Puts δεξιά)
- Row selection με click anywhere
- Live price με coin logos + pulsing dot
- Sorting σε όλες τις στήλες
- 8 symbols (BTC, ETH, AAPL, SPY, TSLA, NVDA, MSFT, QQQ)
- 12 expiries
- Multi-leg + 4 presets
- Greeks, Capital, Prob ITM
- Educational Analyze modal
- IV Chart modal (Volatility Smile)
- Save/Load/Delete strategies με Postgres
- Execution Instructions + Warnings + Outcomes
- Bilingual (EL/EN)
- Dark/Light theme
- Professional UI (Inter + JetBrains Mono)
- Deployed στο Render

Status: COMPLETE (Stage 29)