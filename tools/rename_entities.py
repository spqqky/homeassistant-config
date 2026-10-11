"""Μαζική μετονομασία entity IDs μέσω του websocket API του Home Assistant.

Χρησιμοποιεί το ίδιο call με το UI (config/entity_registry/update), οπότε το HA
μεταφέρει κανονικά ιστορικό, statistics και ρυθμίσεις exposure.

Χρήση (από τη ρίζα του repo):
    pip install websockets
    $env:HA_TOKEN = "<long-lived access token>"
    python tools/rename_entities.py docs/step3_entity_renames.csv            # dry run
    python tools/rename_entities.py docs/step3_entity_renames.csv --apply    # εφαρμογή

Long-lived token: HA → Profile → Security → Long-lived access tokens → Create.
"""
import asyncio
import csv
import json
import os
import sys

import websockets

HA_URL = os.environ.get("HA_URL", "ws://192.168.1.69:8123/api/websocket")


async def main(csv_path: str, apply: bool) -> int:
    token = os.environ.get("HA_TOKEN")
    if not token:
        print("Λείπει το HA_TOKEN.")
        return 2

    with open(csv_path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    async with websockets.connect(HA_URL, max_size=None) as ws:
        await ws.recv()
        await ws.send(json.dumps({"type": "auth", "access_token": token}))
        auth = json.loads(await ws.recv())
        if auth.get("type") != "auth_ok":
            print("Αποτυχία auth:", auth)
            return 2

        msg_id = 0

        async def call(payload):
            nonlocal msg_id
            msg_id += 1
            payload["id"] = msg_id
            await ws.send(json.dumps(payload))
            while True:
                r = json.loads(await ws.recv())
                if r.get("id") == msg_id:
                    return r

        reg = await call({"type": "config/entity_registry/list"})
        existing = {e["entity_id"] for e in reg["result"]}

        ok = skip = fail = 0
        for r in rows:
            old, new, name = r["old_entity_id"], r["new_entity_id"], r.get("new_name") or ""
            if old not in existing:
                if new in existing:
                    print(f"  ήδη έγινε  {old} -> {new}")
                    skip += 1
                else:
                    print(f"  ΛΕΙΠΕΙ     {old}")
                    fail += 1
                continue
            if old != new and new in existing:
                print(f"  ΣΥΓΚΡΟΥΣΗ  {new} υπάρχει ήδη")
                fail += 1
                continue

            payload = {"type": "config/entity_registry/update", "entity_id": old}
            if old != new:
                payload["new_entity_id"] = new
            if name:
                payload["name"] = name
            label = f"{old} -> {new}" + (f'  [name: "{name}"]' if name else "")

            if not apply:
                print(f"  dry-run    {label}")
                ok += 1
                continue

            res = await call(payload)
            if res.get("success"):
                print(f"  OK         {label}")
                ok += 1
            else:
                print(f"  ΣΦΑΛΜΑ     {label}: {res.get('error')}")
                fail += 1
                break  # σταματάμε στο πρώτο λάθος

        mode = "ΕΦΑΡΜΟΓΗ" if apply else "DRY RUN"
        print(f"\n{mode}: {ok} ok, {skip} ήδη έγιναν, {fail} προβλήματα")
        return 1 if fail else 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(asyncio.run(main(sys.argv[1], "--apply" in sys.argv)))
