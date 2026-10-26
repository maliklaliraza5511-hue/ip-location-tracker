"""Core lookup, SQLite history, and report export for IP Location Tracker."""
from __future__ import annotations

import csv
import ipaddress
import json
import sqlite3
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
REPORT_DIR = DATA_DIR / "reports"
DB_PATH = DATA_DIR / "history.sqlite3"
API_BASE = "https://ipwho.is/"

def init_storage() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS lookups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                looked_up_at TEXT NOT NULL,
                ip TEXT NOT NULL,
                country TEXT, region TEXT, city TEXT,
                isp TEXT, organization TEXT, asn TEXT,
                latitude REAL, longitude REAL, timezone TEXT,
                raw_json TEXT NOT NULL
            )
        """)
        db.commit()

def lookup_ip(value: str) -> dict[str, Any]:
    """Look up a public global IP. Returns normalized details or raises ValueError/RuntimeError."""
    try:
        address = ipaddress.ip_address(value.strip())
    except ValueError as exc:
        raise ValueError("Valid IPv4 or IPv6 address enter karein.") from exc
    if not address.is_global:
        raise ValueError("Sirf public, globally routable IP addresses lookup kiye ja sakte hain.")

    request = urllib.request.Request(
        API_BASE + str(address),
        headers={"User-Agent": "IP-Location-Tracker/2.0"}
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Lookup API HTTP error: {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise RuntimeError(f"Network/API request failed: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError("Lookup API ne valid JSON return nahi kiya.") from exc

    if not isinstance(payload, dict):
        raise RuntimeError("Lookup API response format invalid hai.")
    if not payload.get("success", False):
        raise RuntimeError(str(payload.get("message", "Lookup API failed.")))

    conn = payload.get("connection") or {}
    tz = payload.get("timezone") or {}
    result = {
        "looked_up_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "ip": payload.get("ip", str(address)),
        "version": payload.get("type", "N/A"),
        "country": payload.get("country", "N/A"),
        "region": payload.get("region", "N/A"),
        "city": payload.get("city", "N/A"),
        "postal_code": payload.get("postal", "N/A"),
        "isp": conn.get("isp", "N/A"),
        "organization": conn.get("org", "N/A"),
        "asn": conn.get("asn", "N/A"),
        "latitude": payload.get("latitude"),
        "longitude": payload.get("longitude"),
        "timezone": tz.get("id", "N/A"),
    }
    init_storage()
    with sqlite3.connect(DB_PATH) as db:
        cursor = db.execute("""
            INSERT INTO lookups
            (looked_up_at, ip, country, region, city, isp, organization, asn,
             latitude, longitude, timezone, raw_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            result["looked_up_at"], result["ip"], result["country"], result["region"],
            result["city"], result["isp"], result["organization"], str(result["asn"]),
            result["latitude"], result["longitude"], result["timezone"],
            json.dumps(result, ensure_ascii=False)
        ))
        result["id"] = cursor.lastrowid
        db.commit()
    save_reports(result)
    return result

def save_reports(result: dict[str, Any]) -> list[Path]:
    init_storage()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    paths = [
        REPORT_DIR / f"ip_report_{stamp}.json",
        REPORT_DIR / f"ip_report_{stamp}.txt",
        REPORT_DIR / f"ip_report_{stamp}.csv",
    ]
    paths[0].write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    paths[1].write_text("\n".join(f"{k}: {v}" for k, v in result.items()) + "\n", encoding="utf-8")
    with paths[2].open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result.keys()))
        writer.writeheader()
        writer.writerow(result)
    return paths

def get_history(limit: int = 50) -> list[dict[str, Any]]:
    init_storage()
    limit = max(1, min(int(limit), 200))
    with sqlite3.connect(DB_PATH) as db:
        db.row_factory = sqlite3.Row
        rows = db.execute("""
            SELECT id, looked_up_at, ip, country, region, city, isp, organization,
                   asn, latitude, longitude, timezone
            FROM lookups ORDER BY id DESC LIMIT ?
        """, (limit,)).fetchall()
    return [dict(row) for row in rows]

def get_latest_report() -> str | None:
    init_storage()
    files = sorted(REPORT_DIR.glob("ip_report_*.txt"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0].read_text(encoding="utf-8") if files else None
