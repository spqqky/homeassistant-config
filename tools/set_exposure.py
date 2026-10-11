"""Ορίζει ακριβώς ποια entities είναι exposed στο Assist (conversation).

Διαβάζει ένα αρχείο με ένα entity_id ανά γραμμή (# για σχόλια). Αυτά γίνονται exposed και
όλα τα υπόλοιπα un-exposed. Χρησιμοποιεί το ίδιο websocket API με το UI.

Χρήση (από τη ρίζα του repo):
    export HA_TOKEN='...'
    python3 tools/set_exposure.py config/assist_exposed.txt            # dry run
    python3 tools/set_exposure.py config/assist_exposed.txt --apply    # εφαρμογή
"""
import asyncio
import json
import os
import sys

import websockets

HA_URL = os.environ.get("HA_URL", "ws://192.168.1.69:8123/api/websocket")
ASSISTANT = "conversation"


def read_list(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.split("#", 1)[0].strip()
            if line:
                out.append(line)
    return out


async def main(path, apply):
    token = os.environ.get("HA_TOKEN")
    if not token:
        print("Λείπει το HA_TOKEN.")
        return 2
    wanted = set(read_list(path))

    async with websockets.connect(HA_URL, max_size=None) as ws:
        await ws.recv()
        await ws.send(json.dumps({"type": "auth", "access_token": token}))
        if json.loads(await ws.recv()).get("type") != "auth_ok":
            print("Αποτυχία auth")
            return 2
        mid = 0

        async def call(payload):
            nonlocal mid
            mid += 1
            payload["id"] = mid
            await ws.send(json.dumps(payload))
            while True:
                r = json.loads(await ws.recv())
                if r.get("id") == mid:
                    return r

        reg = await call({"type": "config/entity_registry/list"})
        known = {e["entity_id"] for e in reg["result"]}
        missing = sorted(wanted - known)
        if missing:
            print("ΔΕΝ ΥΠΑΡΧΟΥΝ στο registry (διόρθωσε τη λίστα):")
            for m in missing:
                print("   ", m)
            return 1

        cur = await call({"type": "homeassistant/expose_entity/list"})
        exposed = {
            eid for eid, a in cur["result"]["exposed_entities"].items() if a.get(ASSISTANT)
        }
        to_expose = sorted(wanted - exposed)
        to_hide = sorted(exposed - wanted)

        print(f"Τώρα exposed: {len(exposed)} · στόχος: {len(wanted)}")
        for e in to_expose:
            print("   + expose  ", e)
        for e in to_hide:
            print("   - unexpose", e)
        if not apply:
            print("\nDRY RUN: τίποτα δεν άλλαξε.")
            return 0

        for ids, flag in ((to_expose, True), (to_hide, False)):
            if not ids:
                continue
            r = await call(
                {
                    "type": "homeassistant/expose_entity",
                    "assistants": [ASSISTANT],
                    "entity_ids": ids,
                    "should_expose": flag,
                }
            )
            if not r.get("success"):
                print("ΣΦΑΛΜΑ:", r.get("error"))
                return 1
        print(f"\nΕΦΑΡΜΟΓΗ: +{len(to_expose)} / -{len(to_hide)}")
        return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(asyncio.run(main(sys.argv[1], "--apply" in sys.argv)))
