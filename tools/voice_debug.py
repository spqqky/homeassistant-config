"""Τελευταίες φωνητικές εντολές ανά pipeline: τι άκουσε το STT, πόσο πήρε, τι απάντησε, πού χάλασε.

Το HA κρατά στη μνήμη τα τελευταία ~10 runs ανά pipeline (χάνονται με restart).

Χρήση (από τη ρίζα του repo):
    export HA_TOKEN='...'
    python3 tools/voice_debug.py                 # όλα τα pipelines, 5 τελευταία runs
    python3 tools/voice_debug.py pink -n 10      # μόνο pipelines που περιέχουν «pink» στο όνομα
"""
import argparse
import asyncio
import json
import os
from datetime import datetime

import websockets

HA_URL = os.environ.get("HA_URL", "ws://192.168.1.69:8123/api/websocket")


def ts(s):
    try:
        return datetime.fromisoformat(s)
    except (TypeError, ValueError):
        return None


def secs(a, b):
    if a and b:
        return f"{(b - a).total_seconds():.1f}s"
    return "-"


async def main(args):
    token = os.environ.get("HA_TOKEN")
    if not token:
        print("Λείπει το HA_TOKEN.")
        return 2
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
                    return r.get("result") if r.get("success") else None

        pl = await call({"type": "assist_pipeline/pipeline/list"})
        for p in pl["pipelines"]:
            if args.filter and args.filter.lower() not in p["name"].lower():
                continue
            runs = await call({"type": "assist_pipeline/pipeline_debug/list", "pipeline_id": p["id"]})
            runs = (runs or {}).get("pipeline_runs", [])
            if not runs:
                continue
            print(f"\n=== {p['name']}  (STT {p.get('stt_engine')}, agent {p.get('conversation_engine')}) ===")
            for r in runs[-args.n:]:
                dbg = await call({"type": "assist_pipeline/pipeline_debug/get", "pipeline_id": p["id"],
                                  "pipeline_run_id": r["pipeline_run_id"]})
                ev = {}
                err = None
                for e in (dbg or {}).get("events", []):
                    ev.setdefault(e["type"], e)
                    if e["type"] == "error":
                        err = e.get("data", {})
                t = {k: ts(v.get("timestamp")) for k, v in ev.items()}
                text = (ev.get("stt-end", {}).get("data") or {}).get("stt_output", {}).get("text")
                intent = (ev.get("intent-end", {}).get("data") or {}).get("intent_output") or {}
                resp = intent.get("response", {})
                speech = resp.get("speech", {}).get("plain", {}).get("speech")
                local = (ev.get("intent-end", {}).get("data") or {}).get("processed_locally")
                start = t.get("run-start")
                print(f"\n  {start:%H:%M:%S}" if start else "\n  ?")
                print(f"    άκουσε   : {text!r}")
                print(f"    χρόνοι   : ομιλία {secs(t.get('stt-vad-start'), t.get('stt-vad-end'))} · "
                      f"STT {secs(t.get('stt-start'), t.get('stt-end'))} · "
                      f"intent {secs(t.get('intent-start'), t.get('intent-end'))} · "
                      f"TTS {secs(t.get('tts-start'), t.get('tts-end'))}")
                if intent:
                    how = "τοπικά (sentence/automation)" if local else "agent (LLM ή default)"
                    print(f"    απάντηση : {speech!r}  [{resp.get('response_type')}, {how}]")
                if err:
                    print(f"    ΣΦΑΛΜΑ   : {err.get('code')}: {err.get('message')}")
                if "stt-vad-start" not in ev and "stt-start" in ev:
                    print("    ΠΡΟΣΟΧΗ  : δεν υπάρχει stt-vad-start (το μικρόφωνο δεν έστειλε ομιλία)")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("filter", nargs="?", default="")
    ap.add_argument("-n", type=int, default=5)
    raise SystemExit(asyncio.run(main(ap.parse_args())))
