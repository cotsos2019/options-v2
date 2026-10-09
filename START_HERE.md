# 🚀 Πώς να συνεχίσεις αυτό το project

## Αν κλείσει το chat και θες να συνεχίσεις

Αντίγραψε και στείλε αυτό σε νέο chat:

---

"Έχω ένα project Options Dashboard v2. Διάβασε το αρχείο
C:\Users\Administrator\projects\options-v2\NOTES_FOR_DEVELOPER.md
για να καταλάβεις τι κάνει.

Τοπικά τρέχει στο http://127.0.0.1:8051 με:

cd C:\Users\Administrator\projects\options-v2
.venv\Scripts\Activate.ps1
python app.py

Live URL: https://options-v2.onrender.com

Το επόμενο που θέλω να κάνουμε είναι: [ΠΕΡΙΓΡΑΨΕ ΕΔΩ]

Ξεκίνα βήμα-βήμα, μην αλλάξεις πολλά μαζί."

---

## Αν θέλεις να το τρέξεις από την αρχή σε νέο υπολογιστή

### 1. Εγκατέστησε Python 3.12+
https://python.org/downloads

### 2. Εγκατέστησε Git
https://git-scm.com

### 3. Άνοιξε PowerShell και κατέβασε τον κώδικα
cd C:\Users\Administrator\projects
git clone https://github.com/user5461/options-v2.git
cd options-v2

### 4. Φτιάξε virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

Αν σου βγάλει error για execution policy:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

### 5. Εγκατέστησε τα πακέτα
python -m pip install --upgrade pip
pip install -r requirements.txt

### 6. Τρέξε
python app.py

### 7. Άνοιξε browser
http://127.0.0.1:8051

---

## Πώς να χρησιμοποιήσεις την εφαρμογή

1. Διάλεξε symbol — BTC, ETH (crypto), AAPL, SPY, TSLA (stocks)
2. Διάλεξε expiry — πατάς ένα από τα κουμπιά
3. Το grid φορτώνει options
4. Φιλτράρε — All / Calls / Puts
5. Κλίκαρε μια γραμμή — βλέπεις preview chart
6. Χτίσε στρατηγική:
   - Πάτα + LONG ή + SHORT για να προσθέσεις leg
   - Ή διάλεξε preset: Covered Call / Call Spread / Iron Condor / Straddle
   - Ή + Underlying για long το υποκείμενο
7. Clear All για reset

### Τι σημαίνουν τα χρώματα
- Πράσινα = Calls (δικαίωμα αγοράς)
- Κόκκινα = Puts (δικαίωμα πώλησης)
- Πράσινη γραμμή στο chart = κέρδος
- Κόκκινη γραμμή = ζημιά
- Πορτοκαλί κάθετη = strike
- Μπλε κάθετη = spot price

### Presets
- Covered Call — Long underlying + Short OTM call. Κερδίζεις αν η τιμή μείνει flat.
- Call Spread — Long call + Short call σε μεγαλύτερο strike. Περιορισμένο κέρδος, περιορισμένη ζημιά.
- Iron Condor — 4 legs. Κερδίζεις αν η τιμή μείνει κοντά στο spot.
- Straddle — Long call + Long put στο ίδιο strike. Κερδίζεις αν κουνηθεί πολύ.

---

## Πώς να κάνεις αλλαγές

### Τοπικά
1. Άλλαξε τον κώδικα στο app.py
2. Τρέξε python app.py για να δεις
3. Αν δουλεύει, κάνε commit:

git add .
git commit -m "τι άλλαξες"
git push

4. Το Render κάνει auto-deploy σε 2-3 λεπτά

### Αν κάτι σπάσει
Γύρνα στο τελευταίο working commit:

git log --oneline
git checkout <hash>

Ή:

git revert HEAD
git push

---

## Troubleshooting

Πρόβλημα | Λύση
ModuleNotFoundError | pip install -r requirements.txt
Port already in use | Άλλαξε port στο app.py
Grid άδειο για AAPL/SPY/TSLA | Yahoo rate limit. Περίμενε 5 λεπτά.
Chart δεν φορτώνει | Κλίκαρε γραμμή ή preset
500 error | Πρόσθεσε debug=True στο app.run()
Render αργό (30-60s) | Free tier sleep. Φυσιολογικό.
SSL: CERTIFICATE_VERIFY_FAILED | Το yfinance χρειάζεται _stock_session με verify=False

---

## Σημαντικοί κανόνες

1. Ένα feature τη φορά. Μην προσθέσεις 3 πράγματα μαζί.
2. Δοκίμασε τοπικά πρώτα. Μετά push.
3. Αν σπάσει, γύρνα πίσω. Μη συνεχίσεις να σπας πάνω σε σπασμένο.
4. Κάνε commit συχνά. Κάθε working βήμα = ένα commit.
5. Διάβασε το NOTES_FOR_DEVELOPER.md πριν αλλάξεις κάτι σημαντικό.

---

## Χρήσιμα links
- GitHub repo: https://github.com/user5461/options-v2
- Render dashboard: https://dashboard.render.com
- Live app: https://options-v2.onrender.com

---

## Τι είναι τα options (για αρχάριους)

Option = συμβόλαιο που σου δίνει το δικαίωμα (όχι υποχρέωση) να αγοράσεις ή να πουλήσεις ένα περιουσιακό στοιχείο σε συγκεκριμένη τιμή (strike) μέχρι συγκεκριμένη ημερομηνία (expiry).

Call = δικαίωμα αγοράς. Κερδίζεις αν η τιμή ανέβει πάνω από το strike.
Put = δικαίωμα πώλησης. Κερδίζεις αν η τιμή πέσει κάτω από το strike.

Premium = η τιμή του option (αυτό που πληρώνεις για να το αγοράσεις).
Bid = τιμή που κάποιος είναι διατεθειμένος να αγοράσει.
Ask = τιμή που κάποιος είναι διατεθειμένος να πουλήσει.
IV (Implied Volatility) = πόσο volatile αναμένει η αγορά να είναι το υποκείμενο.
Open Interest (OI) = πόσα contracts είναι ανοιχτά αυτή τη στιγμή.

---

## Βήματα για την επόμενη φορά

Άνοιξε νέο chat και στείλε:

"Έχω ένα project Options Dashboard v2. Διάβασε το
C:\Users\Administrator\projects\options-v2\NOTES_FOR_DEVELOPER.md.
Θέλω να προσθέσουμε: [ΤΙ ΘΕΣ]"

Ο AI θα διαβάσει το αρχείο και θα ξέρει τα πάντα για το project.