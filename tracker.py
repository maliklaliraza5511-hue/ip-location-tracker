#!/usr/bin/env python3
"""Terminal interface for IP Location Tracker."""
import subprocess
import webbrowser
from pathlib import Path
from urllib.parse import urlencode

from tracker_core import REPORT_DIR, get_history, get_latest_report, lookup_ip

R = "\033[91m"
G = "\033[92m"
Y = "\033[93m"
C = "\033[96m"
W = "\033[97m"
RESET = "\033[0m"
BOLD = "\033[1m"

def banner():
    print(C + BOLD + "\n" + "=" * 52)
    print("             IP LOCATION TRACKER")
    print("                KALI LINUX")
    print("=" * 52 + RESET)
    print(G + "[1] " + W + "IP lookup + save TXT/JSON/CSV reports")
    print(G + "[2] " + W + "Open reports folder")
    print(G + "[3] " + W + "View latest report")
    print(G + "[4] " + W + "View lookup history")
    print(G + "[5] " + W + "Open web dashboard")
    print(G + "[6] " + W + "Exit" + RESET)

def pause():
    input("\nEnter dabayein menu par wapas jane ke liye...")

def main():
    while True:
        banner()
        choice = input(Y + "\nOption (1-6): " + RESET).strip()
        if choice == "1":
            value = input("Public IP address: ").strip()
            try:
                result = lookup_ip(value)
                print(C + BOLD + "\n--- IP DETAILS ---" + RESET)
                for key, val in result.items():
                    print(f"{key.replace('_', ' ').title():18}: {val}")
                print(G + "\n[+] TXT, JSON aur CSV reports save ho gayi hain." + RESET)
                lat, lon = result.get("latitude"), result.get("longitude")
                if lat is not None and lon is not None:
                    url = "https://www.openstreetmap.org/?" + urlencode({"mlat": lat, "mlon": lon}) + f"#map=12/{lat}/{lon}"
                    print("Map:", url)
                    if input("Browser mein map kholein? (y/n): ").strip().lower() == "y":
                        webbrowser.open(url)
            except (ValueError, RuntimeError) as exc:
                print(R + f"Error: {exc}" + RESET)
            pause()
        elif choice == "2":
            REPORT_DIR.mkdir(parents=True, exist_ok=True)
            try:
                subprocess.Popen(["xdg-open", str(REPORT_DIR)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print("Reports folder:", REPORT_DIR)
            except OSError as exc:
                print("Folder manually open karein:", exc)
            pause()
        elif choice == "3":
            report = get_latest_report()
            print(report if report else "Abhi koi report nahi.")
            pause()
        elif choice == "4":
            rows = get_history()
            if not rows:
                print("History abhi khaali hai.")
            else:
                for row in rows:
                    print(f'#{row["id"]} | {row["looked_up_at"]} | {row["ip"]} | {row["city"]}, {row["country"]} | {row["isp"]}')
            pause()
        elif choice == "5":
            print("Dashboard start karne ke liye doosre terminal mein: python3 webapp.py")
            webbrowser.open("http://127.0.0.1:5000")
            pause()
        elif choice == "6":
            print(G + "Tool band ho raha hai. Allah Hafiz!" + RESET)
            break
        else:
            print(R + "Ghalat option." + RESET)
            pause()

if __name__ == "__main__":
    main()
