# 📊 SIBA Attendance Tracker

A clean local dashboard that logs in to the SIBA student portal and shows your attendance as simple cards: percentage, present classes, absent classes, and how many of your 12 allowed absences you've used.

> Unofficial student project. Not affiliated with Sukkur IBA University.

<!-- ![Dashboard](docs/screenshots/dashboard.png) -->

## ✨ Features

- **Live attendance** for any semester and subject
- **Accurate percentage** calculated from the portal's attendance records
- **Absence tracker** with 12 boxes showing allowed absences used
- **One saved semester snapshot**, stored in your browser
- **Your password is never stored**, only forwarded to the portal

## 🚀 Quick Start

Requires Python 3.10+ and a SIBA CMS ID.

```bash
git clone https://github.com/Usman-Shah-Rashdi/SIBA-Attendence-Tracker.git
cd SIBA-Attendence-Tracker

python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate

pip install -r requirements.txt
python app.py
```

Open **http://127.0.0.1:5000**, go to **Portal Login**, and sign in.

## ⚙️ Configuration (optional)

| Variable | Default | Purpose |
|----------|---------|---------|
| `FLASK_SECRET_KEY` | random | Signs the session cookie |
| `SIBA_PORTAL_URL` | `http://sibagrades.iba-suk.edu.pk:86/` | Portal address |
| `SIBA_PORTAL_TIMEOUT` | `20` | Request timeout in seconds |

## 🧰 Built With

Flask · Requests · BeautifulSoup · vanilla HTML/CSS/JavaScript

## 🧪 Tests

```bash
python -m unittest test_backend -v
```

## 📖 Documentation

Detailed architecture, API, frontend, testing, security, and troubleshooting notes are in
[`doc/DOCUMENTATION.md`](doc/DOCUMENTATION.md).

## 🔒 Note

Meant to run locally for one user. The portal uses plain HTTP, so use a network you trust and don't expose this app to the internet.

## 📄 License

MIT.
