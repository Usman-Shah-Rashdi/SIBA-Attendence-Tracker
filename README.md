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

## 📁 Project layout

```text
src/siba_attendance_tracker/
├── app.py                 # Local Flask API and dashboard routes
├── desktop.py             # Native PyWebView application entry point
├── portal.py              # SIBA login, postbacks, and HTML parsing
├── static/style.css       # Dashboard styling
└── templates/index.html   # Dashboard UI
tests/                     # Backend and parser tests
packaging/                 # PyInstaller spec and Linux desktop metadata
.github/workflows/         # Linux, Windows, AppImage, and source builds
```

The repository is desktop-focused. The Flask API is embedded inside the
native application and is not a separately deployed web service.

## 🖥️ Build the native desktop app

The PC release is a downloadable native-window executable. It bundles the
Python runtime and starts the local API automatically, so users do not install
Python, run a command, or install a browser extension.

Install the build-only dependencies and create the executable:

```bash
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r desktop-requirements.txt
pyinstaller --clean --noconfirm "packaging/SIBA Attendance Tracker.spec"
```

The resulting executable is in `dist/` (`.exe` on Windows). Builds are
platform-specific, so build a Windows executable on Windows and a Linux
executable on Linux. The first launch may require the operating system's
WebView runtime (Windows WebView2 is normally already installed).

Tagged GitHub releases automatically build and attach both desktop artifacts.
The same workflow can also be started manually from the Actions tab.

This is a bundled Python application rather than a source distribution: the
downloaded program contains its interpreter and dependencies.

Each tagged release provides four downloads:

- `SIBA-Attendance-Tracker-windows.exe`
- `SIBA-Attendance-Tracker-linux.AppImage`
- `SIBA-Attendance-Tracker-linux.tar.gz`
- `SIBA-Attendance-Tracker-source.zip`

The AppImage is the recommended Linux download. It can be run after granting
execute permission:

```bash
chmod +x SIBA-Attendance-Tracker-linux.AppImage
./SIBA-Attendance-Tracker-linux.AppImage
```

If the Linux WebView runtime is unavailable, the application opens the
dashboard in your default browser instead.

The source ZIP is for developers who want to inspect or build the project.

## ⚙️ Configuration (optional)

| Variable | Default | Purpose |
|----------|---------|---------|
| `SIBA_PORTAL_URL` | `http://sibagrades.iba-suk.edu.pk:86/` | Portal address |
| `SIBA_PORTAL_TIMEOUT` | `20` | Request timeout in seconds |

## 🧰 Built With

Flask · Requests · BeautifulSoup · PyWebView · PyInstaller ·
vanilla HTML/CSS/JavaScript

## 🧪 Tests

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## 📖 Documentation

Detailed architecture, API, frontend, testing, security, and troubleshooting notes are in
[`doc/DOCUMENTATION.md`](doc/DOCUMENTATION.md).

## 🔒 Note

Meant to run locally for one user. The portal uses plain HTTP, so use a network you trust and don't expose this app to the internet.
The Android APK will be added as a separate mobile build once the Android
client is implemented. The current desktop executable is not an APK.

## 📄 License

MIT.
