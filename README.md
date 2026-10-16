# Options Dashboard v2

Interactive options analytics dashboard — crypto (Deribit, live) + stocks (yfinance, delayed).

Built with **Dash** + **Plotly** + **AG Grid** + **PostgreSQL**.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Dash](https://img.shields.io/badge/Dash-4.x-green)
![Postgres](https://img.shields.io/badge/PostgreSQL-16-blue)

---

## Features

### 📊 Chain View Grid
- Strike στη μέση (χρυσό), Calls αριστερά, Puts δεξιά
- C Bid / C Ask / C IV / C Δ και P Δ / P IV / P Ask / P Bid
- Row selection με click anywhere
- Sorting σε όλες τις στήλες (1x asc, 2x desc, 3x clear)
- Mono font για νούμερα (JetBrains Mono)

### 💰 Live Prices
- Crypto: live από Deribit
- Stocks: delayed από yfinance
- Pulsing dot + coin logos
- Auto-refresh κάθε 10 δευτερόλεπτα

### 🎯 Multi-leg Strategy Builder
- **Presets**: Covered Call, Call Spread, Iron Condor, Straddle
- **Manual**: + LONG / + SHORT / + Underlying
- Real-time payoff chart
- Greeks (Delta, Gamma, Theta, Vega)
- Capital requirements, Prob ITM

### 📖 Educational Analyze Modal
- Τι είναι το option (CALL vs PUT + moneyness ITM/OTM/ATM)
- Τρέχουσα κατάσταση (intrinsic, time value, break-even)
- Πίνακας δεδομένων με tooltips
- Παραδείγματα σεναρίων
- Greeks explanations
- 4 κουμπιά (BUY/SELL CALL/PUT) με εξηγήσεις

### 📈 IV Chart (Volatility Smile)
- IV per strike
- Spot line

### 💾 Save / Load Strategies
- **PostgreSQL persistence** — δεν χάνονται ποτέ
- Αποθήκευση με όνομα
- Φόρτωση / Διαγραφή
- Multi-strategy support

### 🌍 Bilingual + Theme
- Ελληνικά / Αγγλικά (EL / EN)
- Dark / Light mode

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
