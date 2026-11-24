
import os
import sys
import json
import socket
import ipaddress
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from getpass import getpass

from tracker_core import (
    lookup_ip,
    save_reports,
    get_history,
    get_latest_report,
)

BASE_DIR = Path(__file__).resolve().parent
REPORT_DIR = BASE_DIR / "data" / "reports"

C = "\033[96m"
G = "\033[92m"
Y = "\033[93m"
R = "\033[91m"
W = "\033[97m"
RESET = "\033[0m"
BOLD = "\033[1m"


def banner():
    os.system("clear")
    print(C + BOLD)
    print("=" * 55)
    print("          ALI IP LOCATION & INTELLIGENCE")
    print("=" * 55 + RESET)


def pause():
    input("\nPress Enter to continue...")


def valid_ip(value):
    try:
        return ipaddress.ip_address(value)
    except ValueError:
        print(R + "Invalid IP address." + RESET)
        return None


def get_local_ip():
    print(G + "\n[+] YOUR KALI LINUX IP ADDRESSES\n" + RESET)

    try:
        result = subprocess.run(
            ["ip", "-4", "-brief", "address", "show"],
            capture_output=True,
            text=True,
            check=True
        )

        found = False

        for line in result.stdout.splitlines():
            parts = line.split()

            if len(parts) >= 3 and parts[0] != "lo":
                print(G + line + RESET)
                found = True

        if not found:
            print(Y + "No IPv4 address found." + RESET)

    except (FileNotFoundError, subprocess.CalledProcessError) as error:
        print(R + f"Error: {error}" + RESET)


def public_ip_lookup():
    ip = input("\nEnter public IP address: ").strip()
    address = valid_ip(ip)

    if address is None:
        return

    if not address.is_global:
        print(Y + "Please enter a globally routable public IP." + RESET)
        return

    try:
        result = lookup_ip(str(address))
        print(json.dumps(result, indent=4, default=str))
        save_reports(result)
        print(G + "\nReports saved successfully." + RESET)

    except Exception as error:
        print(R + f"Lookup error: {error}" + RESET)


def reverse_dns():
    ip = input("\nEnter IP address: ").strip()
    address = valid_ip(ip)

    if address is None:
        return

    try:
        hostname, aliases, addresses = socket.gethostbyaddr(str(address))
        print(G + "\nHostname: " + hostname + RESET)
        print("Aliases:", aliases)
        print("Addresses:", addresses)

    except (socket.herror, socket.gaierror, OSError) as error:
        print(Y + f"Reverse DNS lookup failed: {error}" + RESET)


def vpn_detection():
    ip = input("\nEnter public IP address: ").strip()
    address = valid_ip(ip)

    if address is None or not address.is_global:
        print(Y + "Enter a valid public IP address." + RESET)
        return

    try:
        result = lookup_ip(str(address))
        data = result.get("data", result) if isinstance(result, dict) else {}
        security = data.get("security", {}) if isinstance(data, dict) else {}

        if not security:
            print(Y + "VPN/security details are not provided by the current API." + RESET)
            return

        print(G + "\nVPN / PROXY / TOR INFORMATION" + RESET)

        for key in ("vpn", "proxy", "tor", "relay", "hosting"):
            print(f"{key.upper()}: {security.get(key, 'Unknown')}")

    except Exception as error:
        print(R + f"Detection error: {error}" + RESET)


def reputation_check():
    ip = input("\nEnter public IP address: ").strip()
    address = valid_ip(ip)

    if address is None or not address.is_global:
        print(Y + "Enter a valid public IP address." + RESET)
        return

    api_key = getpass("Enter your AbuseIPDB API key: ").strip()

    if not api_key:
        print(Y + "API key is required." + RESET)
        return

    url = (
        "https://api.abuseipdb.com/api/v2/check"
        f"?ipAddress={address}&maxAgeInDays=90"
    )

    request = urllib.request.Request(
        url,
        headers={
            "Key": api_key,
            "Accept": "application/json"
        }
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            data = json.loads(response.read().decode())

        details = data.get("data", {})

        print(G + "\nIP REPUTATION RESULTS" + RESET)
        print("IP:", details.get("ipAddress"))
        print("Abuse Score:", details.get("abuseConfidenceScore"))
        print("Total Reports:", details.get("totalReports"))
        print("Country:", details.get("countryCode"))
        print("ISP:", details.get("isp"))

    except urllib.error.HTTPError as error:
        print(R + f"API error: HTTP {error.code}" + RESET)
        print(error.read().decode(errors="replace"))

    except Exception as error:
        print(R + f"Reputation check failed: {error}" + RESET)


def interface_info():
    print(G + "\nNETWORK INTERFACE INFORMATION\n" + RESET)

    try:
        subprocess.run(["ip", "-brief", "address", "show"], check=True)
        print("\nDefault route:")
        subprocess.run(["ip", "route"], check=True)

    except (FileNotFoundError, subprocess.CalledProcessError) as error:
        print(R + f"Error: {error}" + RESET)


def open_reports():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        subprocess.Popen(["xdg-open", str(REPORT_DIR)])
        print(G + "Reports folder opened." + RESET)
    except FileNotFoundError:
        print(Y + f"Reports folder: {REPORT_DIR}" + RESET)


def latest_report():
    report = get_latest_report()

    if not report:
        print(Y + "No report found." + RESET)
    else:
        print(json.dumps(report, indent=4, default=str))


def history():
    records = get_history()

    if not records:
        print(Y + "No lookup history found." + RESET)
        return

    print(G + "\nLOOKUP HISTORY\n" + RESET)

    for record in records:
        print(record)


def ip_type_detection():
    ip = input("\nEnter any IP address: ").strip()
    address = valid_ip(ip)

    if address is None:
        return

    print(G + "\n========== IP INFORMATION ==========" + RESET)
    print("IP Address:", address)
    print("IP Version:", address.version)

    if address.is_private:
        print(Y + "IP Type: PRIVATE" + RESET)
        print("Geolocation: Not available through public IP lookup")
        print("Network: Private/local network")

    elif address.is_global:
        print(G + "IP Type: PUBLIC" + RESET)

        try:
            result = lookup_ip(str(address))
            print(json.dumps(result, indent=4, default=str))
            save_reports(result)
            print(G + "\nReport saved successfully." + RESET)

        except Exception as error:
            print(R + f"Lookup error: {error}" + RESET)

    elif address.is_loopback:
        print(Y + "IP Type: LOOPBACK" + RESET)

    else:
        print(Y + "IP Type: SPECIAL / NON-GLOBAL" + RESET)


def menu():
    while True:
        banner()

        print(W + """
 [1]  My Kali IP Address
 [2]  Public IP Lookup
 [3]  Reverse DNS Lookup
 [4]  VPN / Proxy / Tor Detection
 [5]  IP Reputation Check
 [6]  Network Interface Information
 [7]  Open Reports Folder
 [8]  View Latest Report
 [9]  View Lookup History
 [10] Public / Private IP Detection
 [11] Exit
""" + RESET)

        choice = input(C + "Select option (1-11): " + RESET).strip()

        actions = {
            "1": get_local_ip,
            "2": public_ip_lookup,
            "3": reverse_dns,
            "4": vpn_detection,
            "5": reputation_check,
            "6": interface_info,
            "7": open_reports,
            "8": latest_report,
            "9": history,
            "10": ip_type_detection,
        }

        if choice == "11":
            print(G + "\nALI IP Intelligence Closed." + RESET)
            sys.exit(0)

        action = actions.get(choice)

        if action:
            try:
                action()
            except Exception as error:
                print(R + f"Unexpected error: {error}" + RESET)
        else:
            print(R + "Invalid option. Select 1-11." + RESET)

        pause()


if __name__ == "__main__":
    menu()
