Options Dashboard v2
Interactive options analytics dashboard — crypto (Deribit, live) + stocks (yfinance, delayed).

Built with Dash + Plotly + AG Grid + PostgreSQL.

https://img.shields.io/badge/Python-3.12-blue
https://img.shields.io/badge/Dash-4.x-green
https://img.shields.io/badge/PostgreSQL-16-blue

Features
📊 Chain View Grid
Strike στη μέση (χρυσό), Calls αριστερά, Puts δεξιά

C Bid / C Ask / C IV / C Δ και P Δ / P IV / P Ask / P Bid

- **VOL + OI** (Volume & Open Interest) δίπλα στο Strike
- **30 strikes** — τα πιο κοντινά στο spot

Row selection με click anywhere

Sorting σε όλες τις στήλες (1x asc, 2x desc, 3x clear)

Mono font για νούμερα (JetBrains Mono)

💰 Live Prices
Crypto: live από Deribit

Stocks: delayed από yfinance

Pulsing dot + coin logos

Auto-refresh κάθε 10 δευτερόλεπτα

🎯 Multi-leg Strategy Builder
Presets: Covered Call, Call Spread, Iron Condor, Straddle

Manual: + LONG / + SHORT / + Underlying

Real-time payoff chart

Greeks (Delta, Gamma, Theta, Vega)

Capital requirements, Prob ITM

📖 Educational Analyze Modal
Τι είναι το option (CALL vs PUT + moneyness ITM/OTM/ATM)

Τρέχουσα κατάσταση (intrinsic, time value, break-even)

Πίνακας δεδομένων με tooltips

Παραδείγματα σεναρίων

Greeks explanations

4 κουμπιά (BUY/SELL CALL/PUT) με εξηγήσεις

📈 IV Chart (Volatility Smile)
IV per strike

Spot line

💾 Save / Load Strategies
PostgreSQL persistence — δεν χάνονται ποτέ

Αποθήκευση με όνομα

Φόρτωση / Διαγραφή

Multi-strategy support

### 📊 Chart Modal
- Κλίκαρε γραμμή → πάτα **📊 Chart**
- Ανοίγει payoff chart για το strike

🌍 Bilingual + Theme
Ελληνικά / Αγγλικά (EL / EN)

Dark / Light mode

---

## Tech Stack

- **Python** 3.12
- **Dash** 4.x
- **dash-ag-grid** 35.x
- **Plotly** 7.x
- **PostgreSQL** + psycopg2-binary
- **yfinance** + curl_cffi
- **Deribit API** (public)
- **gunicorn**

---

## Quick Start (Local)

### 1. Clone
```bash
git clone https://github.com/cotsos2019/options-v2.git
cd options-v2
2. Virtual environment
bash
python -m venv .venv
.venv\Scripts\Activate.ps1    # Windows
# source .venv/bin/activate    # Linux/Mac
3. Install
bash
pip install -r requirements.txt
4. PostgreSQL setup
bash
psql -U postgres
CREATE DATABASE options_db;
\q
5. Create .env
text
DB_HOST=localhost
DB_PORT=5432
DB_NAME=options_db
DB_USER=postgres
DB_PASSWORD=your_password
6. Init DB
bash
python -c "import db; db.init_db()"
7. Run
bash
python app.py
Open http://127.0.0.1:8051

Project Structure
text
options-v2/
├── app.py
├── db.py
├── .env
├── requirements.txt
├── Procfile
├── runtime.txt
├── NOTES_FOR_DEVELOPER.md
├── START_HERE.md
└── README.md
Supported Symbols
Crypto (live — Deribit)

BTC ₿, ETH Ξ

**Stocks (delayed — yfinance)**
- AAPL, SPY, TSLA, NVDA, MSFT, QQQ

---

## Contract Sizes

| Type | Size |
|---|---|
| Crypto (BTC, ETH) | 0.1 BTC/ETH per contract |
| Stocks | 100 shares per contract |

---

## Deployment

Deployed on **Render** (free tier). Auto-deploy on push to `main`.

For Postgres on production, use **Neon** or **Render PostgreSQL**.

---

## Documentation

- **[START_HERE.md](START_HERE.md)** — User guide + troubleshooting
- **[NOTES_FOR_DEVELOPER.md](NOTES_FOR_DEVELOPER.md)** — Architecture, gotchas, stage history

---

## License

Personal project — educational use.
