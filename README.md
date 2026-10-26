# IP Location Tracker (Kali Linux)

A Python IP geolocation utility with both a terminal interface and a local web dashboard.

## Features
- Public IPv4/IPv6 lookup via `ipwho.is`
- Country, region, city, ISP, organization, ASN, timezone and approximate coordinates
- Local SQLite lookup history
- TXT, JSON and CSV reports
- OpenStreetMap link in CLI and interactive Leaflet map in the dashboard
- No third-party Python dependency for CLI; Flask is used for the dashboard

## Requirements
- Python 3.10+
- Internet access for lookups and map tiles
- `ipwho.is` availability

## Install on Kali Linux
```bash
cd ~/ip-location-tracker
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python3 -m py_compile tracker.py tracker_core.py webapp.py
```

If virtual environment creation is blocked, install Kali's package first:
```bash
sudo apt update
sudo apt install python3-venv
```

## Run terminal mode
```bash
source .venv/bin/activate
python3 tracker.py
```

## Run web dashboard
In terminal 1:
```bash
cd ~/ip-location-tracker
source .venv/bin/activate
python3 webapp.py
```
Open `http://127.0.0.1:5000` in the browser. The server is bound to localhost only.

## Storage
- SQLite history: `data/history.sqlite3`
- Reports: `data/reports/`

These are intentionally ignored by Git to avoid committing lookup history or personal data.

## Tests
```bash
source .venv/bin/activate
python3 -m unittest discover -s tests -v
```

## GitHub upload
Review changes first:
```bash
git status
git diff
```
After you have tested the app:
```bash
git add tracker.py tracker_core.py webapp.py requirements.txt README.md .gitignore tests
git commit -m "Upgrade IP tracker with dashboard and history"
git push origin main
```
Do not add `data/` or any private lookup reports. If you want to retain your old code, keep `tracker.py.backup` local and do not stage it unless you explicitly want that backup in the repository.

## Privacy and accuracy
IP geolocation is approximate; it does not reveal a person's exact home address. Each lookup sends the requested IP to the third-party `ipwho.is` API. Results and reports are saved locally. Use this tool only for lawful, authorized lookups.
