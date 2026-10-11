"""Καταγραφή Assist pipelines, satellites και μηχανών STT/TTS/conversation.

Χρήση (από τη ρίζα του repo):
    export HA_TOKEN='...'
    python3 tools/pipelines_dump.py            # εκτύπωση
    python3 tools/pipelines_dump.py --save     # και αποθήκευση σε docs/pipelines.json
"""
import asyncio
import json
import os
import sys

import websockets

HA_URL = os.environ.get("HA_URL", "ws://192.168.1.69:8123/api/websocket")


async def main(save):
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
                    return r.get("result")

        pl = await call({"type": "assist_pipeline/pipeline/list"})
        states = await call({"type": "get_states"})
        entries = await call({"type": "config_entries/get"})

    by_id = {p["id"]: p for p in pl["pipelines"]}
    preferred = pl.get("preferred_pipeline")

    print("== Pipelines ==")
    for p in pl["pipelines"]:
        star = " (preferred)" if p["id"] == preferred else ""
        print(f"\n[{p['name']}]{star}  id={p['id']}")
        print(f"  language      : {p.get('language')}")
        print(f"  conversation  : {p.get('conversation_engine')}  lang={p.get('conversation_language')}  "
              f"prefer_local={p.get('prefer_local_intents')}")
        print(f"  stt           : {p.get('stt_engine')}  lang={p.get('stt_language')}")
        print(f"  tts           : {p.get('tts_engine')}  lang={p.get('tts_language')}  voice={p.get('tts_voice')}")
        print(f"  wake word     : {p.get('wake_word_entity')} {p.get('wake_word_id') or ''}")

    print("\n== Satellites: επιλεγμένο pipeline ==")
    for s in states:
        eid = s["entity_id"]
        if eid.startswith("select.") and ("assistant" in eid or "pipeline" in eid) and "options" in s["attributes"]:
            opts = s["attributes"]["options"]
            if any(o in opts for o in ("preferred",)) or any(o in [p["name"] for p in by_id.values()] for o in opts):
                print(f"  {eid:<60} → {s['state']}")
        if eid.startswith("select.") and ("finished_speaking" in eid or "vad" in eid):
            print(f"  {eid:<60} = {s['state']}")

    print("\n== Μηχανές ==")
    for dom in ("stt", "tts", "conversation", "wake_word"):
        ids = sorted(s["entity_id"] for s in states if s["entity_id"].startswith(dom + "."))
        print(f"  {dom:<12}: {', '.join(ids)}")

    print("\n== Integrations φωνής ==")
    for e in entries:
        if e["domain"] in ("google_generative_ai_conversation", "google_cloud", "cloud", "wyoming",
                           "openai_conversation", "anthropic", "ollama", "speech_to_phrase", "mic_to_mediaplayer"):
            print(f"  {e['domain']:<36} {e['title']}  ({e['state']})")

    if save:
        os.makedirs("docs", exist_ok=True)
        with open("docs/pipelines.json", "w", encoding="utf-8") as f:
            json.dump({"preferred": preferred, "pipelines": pl["pipelines"]}, f, ensure_ascii=False, indent=2)
        print("\nΑποθηκεύτηκε: docs/pipelines.json")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main("--save" in sys.argv)))
