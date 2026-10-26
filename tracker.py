import urllib.request
import json
import ipaddress
import webbrowser
import os
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode

# Terminal colors
R = "\033[91m"
G = "\033[92m"
Y = "\033[93m"
B = "\033[94m"
C = "\033[96m"
M = "\033[95m"
W = "\033[97m"
RESET = "\033[0m"
BOLD = "\033[1m"

REPORT_DIR = Path.home() / "ip-tracker" / "reports"


def banner():
    os.system("clear")
    print(C + BOLD + "=" * 48)
    print("       IP LOCATION TRACKER")
    print("          KALI LINUX")
    print("=" * 48 + RESET)
    print(G + "  [1] " + W + "IP Address Lookup")
    print(G + "  [2] " + W + "Open Saved Reports Folder")
    print(G + "  [3] " + W + "View Latest Report")
    print(G + "  [4] " + W + "Exit")
    print(C + "=" * 48 + RESET)


def track_ip(ip):
    try:
        address = ipaddress.ip_address(ip)

        if not address.is_global:
            print(R + "Public IP address enter karein." + RESET)
            return

        url = f"https://ipwho.is/{address}"
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "IP-Location-Tracker/1.0"}
        )

        with urllib.request.urlopen(request, timeout=15) as response:
            data = json.loads(response.read().decode())

        if not data.get("success", False):
            print(R + "Lookup error: " +
                  str(data.get("message", "Unknown error")) + RESET)
            return

        lat = data.get("latitude")
        lon = data.get("longitude")
        isp = data.get("connection", {}).get("isp", "N/A")

        print("\n" + C + BOLD + "--- IP DETAILS ---" + RESET)
        print(Y + "IP Address: " + W + str(data.get("ip", "N/A")))
        print(Y + "Country:    " + W + str(data.get("country", "N/A")))
        print(Y + "Region:     " + W + str(data.get("region", "N/A")))
        print(Y + "City:       " + W + str(data.get("city", "N/A")))
        print(Y + "ISP:        " + W + str(isp))
        print(Y + "Latitude:   " + W + str(lat))
        print(Y + "Longitude:  " + W + str(lon) + RESET)

        # TXT report save karein
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        now = datetime.now().astimezone()
        report = f"""IP LOCATION TRACKER REPORT
Date/Time: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}
IP Address: {data.get('ip', 'N/A')}
Country: {data.get('country', 'N/A')}
Region: {data.get('region', 'N/A')}
City: {data.get('city', 'N/A')}
ISP: {isp}
Latitude: {lat}
Longitude: {lon}
"""

        filename = "ip_report_" + now.strftime("%Y%m%d_%H%M%S_%f") + ".txt"
        report_file = REPORT_DIR / filename
        report_file.write_text(report, encoding="utf-8")

        print(G + "\n[+] Report saved: " + str(report_file) + RESET)

        # Map open karein
        if lat is not None and lon is not None:
            map_url = (
                "https://www.openstreetmap.org/?"
                + urlencode({"mlat": lat, "mlon": lon})
                + f"#map=12/{lat}/{lon}"
            )
            print(C + "[+] Map URL: " + map_url + RESET)
            choice = input(Y + "Map browser mein kholein? (y/n): " + RESET)
            if choice.lower() == "y":
                webbrowser.open(map_url)

    except ValueError:
        print(R + "Valid IP address enter karein." + RESET)
    except Exception as error:
        print(R + "Error: " + str(error) + RESET)


def open_reports():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    print(G + "Reports folder: " + str(REPORT_DIR) + RESET)
    try:
        webbrowser.open(REPORT_DIR.as_uri())
        os.system(f'xdg-open "{REPORT_DIR}" >/dev/null 2>&1 &')
    except Exception:
        print(Y + "Folder manually open karein." + RESET)


def latest_report():
    files = sorted(
        REPORT_DIR.glob("ip_report_*.txt"),
        key=lambda f: f.stat().st_mtime,
        reverse=True
    ) if REPORT_DIR.exists() else []

    if not files:
        print(Y + "Abhi koi report save nahi hui." + RESET)
        return

    print(C + "\n--- Latest Report ---" + RESET)
    print(files[0].read_text(encoding="utf-8"))


def main():
    while True:
        banner()
        choice = input(Y + "\nOption select karein: " + RESET).strip()

        if choice == "1":
            ip = input(C + "IP address enter karein: " + RESET).strip()
            track_ip(ip)
            input(G + "\nEnter dabayein menu par wapas jane ke liye..." + RESET)

        elif choice == "2":
            open_reports()
            input(G + "\nEnter dabayein wapas jane ke liye..." + RESET)

        elif choice == "3":
            latest_report()
            input(G + "\nEnter dabayein wapas jane ke liye..." + RESET)

        elif choice == "4":
            print(G + "Tool band ho raha hai. Allah Hafiz!" + RESET)
            break

        else:
            print(R + "Ghalat option! 1 se 4 select karein." + RESET)
            input("Enter dabayein...")


if __name__ == "__main__":
    main()
