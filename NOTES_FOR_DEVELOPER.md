# Notes for AI / Developer

## Project: Options Dashboard v2

### Τι είναι
Dash web app που δείχνει live options data (crypto από Deribit, stocks από yfinance) με multi-leg strategy builder και interactive Plotly charts.

### Live URL
https://options-v2.onrender.com (Render.com free tier)
Τοπικό: http://127.0.0.1:8051

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
- app.py               # ΟΛΟΣ ο κώδικας εδώ (single-file app)
- requirements.txt
- Procfile             # "web: gunicorn app:server"
- runtime.txt          # "python-3.12.3"
- .gitignore
- NOTES_FOR_AI.md      # αυτό
- START_HERE.md        # οδηγίες για τον χρήστη
- .venv/               # τοπικό virtualenv

---

## Data Sources

### Crypto (Live)
- Deribit — https://www.deribit.com/api/v2
- Endpoints:
  - /public/get_instruments?currency=BTC&kind=option&expired=false — λίστα instruments
  - /public/get_book_summary_by_currency?currency=BTC&kind=option — bulk tickers (γρήγορο)
  - /public/get_index_price?index_name=btc_usd — spot price
- ΚΡΙΣΙΜΟ: Τα bid_price/ask_price από το book summary είναι σε BTC, όχι USD. Πολλαπλασιάζονται με το spot για να γίνουν USD.
- ΚΡΙΣΙΜΟ: Instrument name format: BTC-10OCT26-75000-C. Το expiry label εξάγεται από το parts[1].
- ΚΡΙΣΙΜΟ: Το /get_instruments δίνει expiration_timestamp (ms), αλλά το book summary ΔΕΝ το δίνει. Φιλτράρουμε το book summary με string match στο instrument name (-10OCT26-).

### Stocks (Delayed ~15 min)
- yfinance (Yahoo Finance)
- ΚΡΙΣΙΜΟ: Το yfinance στο Windows αποτυγχάνει με SSL error. Λύση: shared session με curl_cffi:
  _stock_session = curl_requests.Session(impersonate="chrome")
  _stock_session.verify = False
  Δημιουργείται ΜΙΑ φορά. ΜΗΝ δημιουργείς νέο session σε κάθε κλήση.
- ΚΡΙΣΙΜΟ: Η μορφή expiry για stocks είναι 2026-10-16 (ISO date), όχι 10OCT26.

---

## Architecture

### Stores (Dash state)
- symbol-store: "BTC" / "ETH" / "AAPL" / "SPY" / "TSLA"
- expiry-store: Ενεργό expiry label
- expiry-list: Λίστα με όλα τα expiries
- legs-store: Legs της στρατηγικής
- filter-store: "all" / "call" / "put"
- rows-store: Όλα τα rows πριν το filter

### Leg format
{
    "side": 1,
    "type": "call",
    "strike": 75000,
    "premium": 1234.56,
    "instrument": "BTC-10OCT26-75000-C"
}

### Row format
{
    "instrument": "BTC-10OCT26-75000-C",
    "type": "call",
    "strike": 75000.0,
    "bid": 1234.56,
    "ask": 1300.00,
    "iv": 55.2,
    "delta": None,
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

---

## UI / Theme
Dark mode only

Χρώματα:
- BG: #0e1117
- Panel: #161b22
- Border: #30363d
- Text: #e6edf3
- Muted: #8b949e
- Calls/Profit: #2ecc71
- Puts/Loss: #e74c3c
- Strike: #f39c12
- Spot: #58a6ff
- Accent: #1f6feb
- Short/Red: #da3633

---

## Γνωστά Gotchas

1. Dash "Duplicate Output" error
   Αν δύο callbacks γράφουν στο ίδιο property, πρέπει allow_duplicate=True.

2. Αριθμός outputs = αριθμός return values
   Αν έχεις 3 Outputs, return 3 τιμές.

3. ALL as dash_all import
   Πρέπει να είναι στην αρχή του αρχείου.

4. Deribit prices
   Σε BTC. Πολλαπλασιασμός με spot.

5. yfinance rate limit
   Ένα shared session. Cache.

6. expiry-store validation
   Πριν φιλτράρεις τα rows, έλεγξε αν το expiry label είναι valid για το τρέχον symbol.

7. Δύο formats
   Crypto: 10OCT26
   Stocks: 2026-10-16

8. Render free tier
   Sleeps after 15 min, 30-60s wake up.

9. Local port
   8051. Στο Render: PORT env variable.

---

## Ιστορικό
Ξεκίνησε ως options-app (παλιό). Ξαναγράφτηκε ως options-v2.

- Stage 1: BTC μόνο, REST API
- Stage 2: + ETH
- Stage 3: + Greeks (αφαιρέθηκαν)
- Stage 4: + Stocks (AAPL, SPY, TSLA)
- Stage 5: + Multi-leg builder
- Stage 6: + Presets + Underlying leg
- Stage 7: Deploy στο Render
- Stage 8: + Filters (All/Calls/Puts) + χρωματισμός
- Stage 9: Μετατροπή crypto prices σε USD

Μάθημα: Χτίσε ένα feature τη φορά.

---

## Τι θα μπορούσε να προστεθεί
- Greeks στο grid για crypto
- Volume στήλη
- Save/load strategies
- Άλλα symbols (NVDA, MSFT, QQQ)
- Light mode
- Mobile responsive
- IV chart per strike
- Black-Scholes Greeks για stocks
- WebSocket αντί για polling
- Backtesting

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
ή
git revert HEAD
git push

---

## Τελευταία κατάσταση
- ✅ BTC, ETH, AAPL, SPY, TSLA
- ✅ Expiry selector, filters, multi-leg, presets
- ✅ Auto-select πρώτης γραμμής
- ✅ Deployed στο Render
- ✅ Crypto bid/ask σε USD