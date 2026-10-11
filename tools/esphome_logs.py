"""Ζωντανά logs από μια ESPHome συσκευή (π.χ. Voice PE), με το κλειδί από το .storage του HA.

Χρήση (από τη ρίζα του repo, με το venv που έχει το aioesphomeapi):
    ~/ha-venv/bin/python tools/esphome_logs.py "Pink Assistant"

Το όνομα είναι ο τίτλος του ESPHome config entry: "Home Assistant", "Nefeli Assistant",
"Alex Assistant", "Pink Assistant". Ctrl+C για έξοδο.
"""
import json
import os
import subprocess
import sys

STORAGE = os.path.join(os.path.dirname(__file__), "..", ".storage", "core.config_entries")


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    title = sys.argv[1]
    with open(STORAGE, encoding="utf-8") as f:
        entries = json.load(f)["data"]["entries"]
    for e in entries:
        if e["domain"] == "esphome" and e["title"] == title:
            host = e["data"]["host"]
            psk = e["data"].get("noise_psk")
            print(f"Σύνδεση σε {title} ({host})… Ctrl+C για έξοδο\n", flush=True)
            cli = os.path.join(os.path.dirname(sys.executable), "aioesphomeapi-logs")
            cmd = [cli, host] + (["--noise-psk", psk] if psk else [])
            try:
                return subprocess.call(cmd)
            except KeyboardInterrupt:
                return 0
    print("Δεν βρέθηκε ESPHome entry με τίτλο:", title)
    print("Διαθέσιμα:", [e["title"] for e in entries if e["domain"] == "esphome"])
    return 1


if __name__ == "__main__":
    sys.exit(main())
