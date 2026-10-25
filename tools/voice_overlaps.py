"""Ελέγχει ποιο automation πιάνει κάθε δοκιμαστική φράση και βρίσκει επικαλύψεις.

Αν μια φράση ταιριάζει σε triggers ΔΥΟ automations, το HA εκτελεί ένα από αυτά, όχι απαραίτητα το σωστό
(π.χ. «σκούπισε το pink radio» πήγε στη σκούπα σπιτιού). Το εργαλείο το εντοπίζει χωρίς HA.

Εγκατάσταση μία φορά (WSL venv): ~/ha-venv/bin/pip install hassil pyyaml
Χρήση (από τη ρίζα του repo):
    ~/ha-venv/bin/python tools/voice_overlaps.py                       # docs/voice_test_sentences.txt
    echo "σκούπισε το σαλόνι" | ~/ha-venv/bin/python tools/voice_overlaps.py -
"""
import glob
import re
import sys

import yaml
from hassil import Intents, WildcardSlotList
from hassil.recognize import recognize_all


class Loader(yaml.SafeLoader):
    pass


Loader.add_multi_constructor("!", lambda loader, suffix, node: None)


def load_intents(root="packages"):
    intents = {}
    for f in glob.glob(f"{root}/**/*.yaml", recursive=True):
        d = yaml.load(open(f, encoding="utf-8"), Loader=Loader) or {}
        for a in d.get("automation") or []:
            for i, t in enumerate(a.get("triggers") or a.get("trigger") or []):
                if (t.get("trigger") or t.get("platform")) != "conversation":
                    continue
                c = t["command"]
                c = [c] if isinstance(c, str) else c
                intents[f"{a.get('alias', a.get('id'))} | {t.get('id', i)}"] = {"data": [{"sentences": c}]}
    names = set()
    for v in intents.values():
        for c in v["data"][0]["sentences"]:
            names |= set(re.findall(r"\{(\w+)", c))
    return Intents.from_dict({"language": "el", "intents": intents}), {n: WildcardSlotList(n) for n in names}


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "docs/voice_test_sentences.txt"
    text = sys.stdin.read() if src == "-" else open(src, encoding="utf-8").read()
    sentences = [s.strip() for s in text.split("\n") if s.strip() and not s.startswith("#")]
    intents, slots = load_intents()
    problems = 0
    for s in sentences:
        trig = sorted({r.intent.name for r in recognize_all(s, intents, slot_lists=slots)})
        autos = {t.split(" | ")[0] for t in trig}
        note = ""
        if not trig:
            note = "   ✗ καμία φράση (πάει στο LLM / «δεν κατάλαβα»)"
        elif len(autos) > 1:
            note, problems = "   ⚠ ΠΟΛΛΑ automations: το HA θα διαλέξει ένα", problems + 1
        elif len(trig) > 1:
            note, problems = "   ⚠ πολλά triggers του ίδιου automation", problems + 1
        print(f"{s!r:52} → {', '.join(trig) or '-'}{note}")
    print(f"\nΕπικαλύψεις: {problems}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
