# 📊 SIBA Attendance Tracker

A clean local dashboard that logs in to the SIBA student portal and shows your attendance as simple cards: percentage, present classes, absent classes, and how many of your 12 allowed absences you've used.

> Unofficial student project. Not affiliated with Sukkur IBA University.

<img width="1352" height="714" alt="image" src="https://github.com/user-attachments/assets/97383563-c463-40c3-8d64-0868384b2866" />

<img width="1348" height="704" alt="image" src="https://github.com/user-attachments/assets/57015aa8-1e61-46b4-85fc-49f8b258ec03" />

<img width="1347" height="707" alt="image" src="https://github.com/user-attachments/assets/c0a489bd-c8cd-4ddf-afb7-ea1fe2847528" />
attendance saved in local memory so its display even when offline

## ✨ Features

- **Live attendance** for any semester and subject
- **Accurate percentage** calculated from the portal's attendance records
- **Absence tracker** with 12 boxes showing allowed absences used
- **One saved semester snapshot**, stored in your browser, with an option to delete it
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
there are things missing that i want to add first is polishing the code and deploying it as a web app.
or an apk release as well.

## 📄 License

MIT.
