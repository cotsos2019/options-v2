# Notes for AI / Developer

## Project: Options Dashboard v2

### Τι είναι
Dash web app που δείχνει live options data (crypto από Deribit, stocks από yfinance) με multi-leg strategy builder, capital/probability analysis, και interactive Plotly charts.

### Live URL
https://options-v2.onrender.com (Render.com free tier)

### Τοπικό URL
http://127.0.0.1:8051

### GitHub
https://github.com/user5461/options-v2

### Φάκελος
C:\Users\Administrator\projects\options-v2

---

## Tech Stack
- Python 3.12.3
- Dash 4.x
- dash-ag-grid
- Plotly
- requests + urllib3
- yfinance + curl_cffi
- gunicorn (production)

## Dependencies (requirements.txt)
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
- app.py                    # ΟΛΟΣ ο κώδικας (single-file app)
- requirements.txt
- Procfile                  # "web: gunicorn app:server"
- runtime.txt               # "python-3.12.3"
- .gitignore
- NOTES_FOR_DEVELOPER.md    # αυτό
- START_HERE.md             # οδηγίες για τον χρήστη
- .venv/                    # τοπικό virtualenv

---

## Data Sources

### Crypto (Live)
- Deribit — https://www.deribit.com/api/v2
- Endpoints:
  - /public/get_instruments?currency=BTC&kind=option&expired=false
  - /public/get_book_summary_by_currency?currency=BTC&kind=option
  - /public/get_index_price?index_name=btc_usd
- ΚΡΙΣΙΜΟ: Τα bid_price/ask_price από το book summary είναι σε BTC, όχι USD. Πολλαπλασιάζονται με το spot για να γίνουν USD.
- ΚΡΙΣΙΜΟ: Instrument name format: BTC-10OCT26-75000-C. Το expiry label εξάγεται από το parts[1].
- ΚΡΙΣΙΜΟ: Το /get_instruments δίνει expiration_timestamp (ms), αλλά το book summary ΔΕΝ το δίνει. Φιλτράρουμε με string match στο instrument name (-10OCT26-).

### Stocks (Delayed ~15 min)
- yfinance (Yahoo Finance)
- ΚΡΙΣΙΜΟ: Το yfinance στο Windows αποτυγχάνει με SSL error. Λύση: shared session με curl_cffi:
  _stock_session = curl_requests.Session(impersonate="chrome")
  _stock_session.verify = False
  Δημιουργείται ΜΙΑ φορά. ΜΗΝ δημιουργείς νέο session σε κάθε κλήση.
- ΚΡΙΣΙΜΟ: Η μορφή expiry για stocks είναι 2026-10-16 (ISO date), όχι 10OCT26.

---

## Contract sizes (ΣΗΜΑΝΤΙΚΟ)
- Crypto (BTC, ETH): 1 option = 1 BTC/ETH
- Stocks (AAPL, SPY, TSLA, NVDA, MSFT, QQQ): 1 option = 100 shares

---

## Architecture

### Stores (Dash state)
- symbol-store: "BTC" / "ETH" / "AAPL" / "SPY" / "TSLA" / "NVDA" / "MSFT" / "QQQ"
- expiry-store: Ενεργό expiry label
- expiry-list: Λίστα με όλα τα expiries (max 12)
- legs-store: Legs της στρατηγικής
- filter-store: "all" / "call" / "put"
- rows-store: Όλα τα rows πριν το filter
- theme-store: "dark" / "light"
- lang-store: "el" / "en"
- about-open, analysis-open: booleans για modals

### Leg format
{
    "side": 1,       # 1=long, -1=short
    "type": "call",  # "call", "put", "underlying"
    "strike": 75000,
    "premium": 1234.56,
    "instrument": "BTC-10OCT26-75000-C"
}

### Row format (chain)
{
    "instrument": "BTC-10OCT26-75000-C",
    "type": "call",
    "strike": 75000.0,
    "bid": 1234.56,           # σε USD
    "ask": 1300.00,
    "premium": 1267.28,       # mid = (bid+ask)/2
    "capital": 1300.00,       # ask (1 contract, 1 BTC ή 100 shares)
    "prob_itm": 0.47,         # Black-Scholes N(d2)
    "iv": 55.2,
    "volume": 12,
    "oi": 123
}

### Cache
In-memory dict _cache με TTL:
- Crypto expiries: 600s
- Crypto chain: 60s
- Crypto spot: 30s
- Stock expiries: 3600s
- Stock chain: 120s
- Stock spot: 60s

### Black-Scholes
Χρησιμοποιείται για Prob ITM: N(d2) για calls, N(-d2) για puts.
r = 0.045 (approximate risk-free rate)

### T = time to expiry
- Για stocks: parsed από ISO date
- Για crypto: parsed από Deribit label (π.χ. 10OCT26)

---

## Features

### 1. Grid (αριστερά, 63% πλάτος)
Στήλες: Instrument, Type, Strike, Bid, Ask, Premium, Capital, Prob ITM, IV, Vol, OI
- Calls: πράσινα, Puts: κόκκινα
- Highlight: πράσινο/κόκκινο background ανάλογα με type

### 2. Chart (δεξιά, 37% πλάτος)
- Preview chart όταν κλικάρεις γραμμή
- Multi-leg payoff όταν έχεις legs

### 3. Presets (auto από spot)
- Covered Call — long underlying + short OTM call
- Call Spread — long call + short higher call
- Iron Condor — 4 legs γύρω από spot
- Straddle — long call + long put στο spot
- ΔΕΝ χρησιμοποιούν την επιλογή σου — χτίζονται αυτόματα με βάση το spot.

### 4. Manual (LONG / SHORT buttons)
- Χρησιμοποιούν τη γραμμή που διάλεξες στο grid.
- Πάτα + LONG ή + SHORT για να προσθέσεις leg.

### 5. Modals
- ❓ Οδηγός Στρατηγικών (γενικές εξηγήσεις)
- 📊 Ανάλυση Στρατηγικής:
  - Τα legs σου
  - ⚙️ Εντολές Εκτέλεσης (BUY/SELL)
  - Απαιτούμενο Κεφάλαιο
  - ⚠️ Προειδοποιήσεις (Covered Call: downside/upside)
  - Σύνοψη: Net cost, Max profit, Max loss
  - Break-even points
  - Chart
  - 6 Σενάρια με πραγματικά νούμερα

### 6. Theme toggle ☀️ / 🌙
Dark mode (default) και Light mode.

### 7. Language toggle 🇬🇷 / 🇬🇧
Ελληνικά (default) και Αγγλικά. Όλα τα labels αλλάζουν.

---

## UI / Theme
Dark mode default
- BG: #0e1117
- Panel: #161b22
- Border: #30363d
- Text: #e6edf3
- Calls/Profit: #2ecc71
- Puts/Loss: #e74c3c
- Strike: #f39c12
- Spot: #58a6ff
- Accent: #1f6feb

Layout:
- grid-template-columns: 1.9fr 1.1fr (grid 63%, chart 37%)
- @media (max-width: 1200px) → stacked

---

## Γνωστά Gotchas

1. Dash "Duplicate Output" error → allow_duplicate=True
2. Αριθμός outputs = αριθμός return values
3. ALL as dash_all import στην αρχή
4. Deribit prices σε BTC → *spot για USD
5. yfinance: shared session + cache
6. expiry-store validation πριν φιλτράρεις
7. Δύο formats: 10OCT26 (crypto), 2026-10-16 (stocks)
8. Render free tier: sleep, 30-60s wake up
9. Local port: 8051, Render: PORT env var
10. Contract sizes: crypto=1, stocks=100

---

## Ιστορικό Stages
- Stage 1: BTC μόνο, REST API
- Stage 2: + ETH
- Stage 3: + Greeks (αφαιρέθηκαν)
- Stage 4: + Stocks (AAPL, SPY, TSLA)
- Stage 5: + Multi-leg builder
- Stage 6: + Presets + Underlying leg
- Stage 7: Deploy στο Render
- Stage 8: + Filters (All/Calls/Puts) + χρωματισμός
- Stage 9: Crypto prices σε USD
- Stage 10: + Volume, νέα symbols (NVDA, MSFT, QQQ), Light mode, responsive
- Stage 11: + Όμορφα buttons (icons, gradients)
- Stage 12: + 12 expiries, δίγλωσσο UI, preset guide
- Stage 13: + Strategy Analysis με πραγματικά νούμερα
- Stage 14: + Ξεχωριστό 📊 κουμπί
- Stage 15: + Hints (auto vs manual)
- Stage 16: + Premium/BE/5 P&L scenarios (αφαιρέθηκε)
- Stage 17A: + Capital Required, Prob ITM, Execution Instructions, Warnings
- Stage 18: Wider grid (63%), narrower chart (37%)

---

## Τι θα μπορούσε να προστεθεί
- Greeks (delta, gamma, theta, vega) — επόμενο
- Save/load strategies (SQLite)
- IV chart per strike (volatility smile)
- WebSocket αντί για REST polling
- Backtesting
- Mobile UI βελτιώσεις

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

## Πώς να κάνεις rollback
git log --oneline
git checkout <hash>

---

## Τελευταία κατάσταση (checkpoint)
- ✅ BTC, ETH, AAPL, SPY, TSLA, NVDA, MSFT, QQQ
- ✅ Expiry selector (12 expiries)
- ✅ Filters (All/Calls/Puts) με χρωματισμό
- ✅ Multi-leg builder
- ✅ Presets (Covered Call, Call Spread, Iron Condor, Straddle)
- ✅ Auto-select πρώτης γραμμής
- ✅ Capital Required, Prob ITM, Premium
- ✅ Execution Instructions + Warnings
- ✅ Bilingual (EL/EN)
- ✅ Dark/Light mode
- ✅ Responsive (stacked < 1200px)
- ✅ Deployed στο Render
- ✅ Wide grid (63%), narrow chart (37%)

**Επόμενο:** Greeks (delta, gamma, theta, vega)