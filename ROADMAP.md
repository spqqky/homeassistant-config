# ROADMAP

Κατάσταση: ⬜ εκκρεμεί · 🔄 σε εξέλιξη · ✅ ολοκληρώθηκε

| # | Βήμα | Κατάσταση | Σημειώσεις |
|---|------|-----------|------------|
| 0 | Workspace: σύνδεση φακέλου, CLAUDE.md, ROADMAP.md, git tag `baseline` | 🔄 | `baseline` → `a67485b` (Initial Home Assistant configuration backup) |
| 1 | Inventory: entities, satellites (hardware, έξοδος ήχου), pipelines, automations, scripts | ⬜ | |
| 2 | Δομή: floors `home` / `pinkradio`, areas, satellites στα areas τους | ⬜ | |
| 3 | Naming cleanup: `pink_radio_*` → `pinkradio_*`, plugs με λειτουργικά ονόματα, grep και διόρθωση σε όλο το YAML | ⬜ | |
| 4 | Μοντέλο ασφαλείας: exposed entities, pipeline του Pink, guards (και MCP, αν το θέλουμε) | ⬜ | |
| 5 | Voice routing core: `script.voice_speak`, default έξοδος ανά assistant | ⬜ | |
| 6 | Ανακοινώσεις: refactor του «Voice - Ανακοινώσεις» | ⬜ | |
| 7 | Home vacuum: ανά δωμάτιο, Basic default, φωνητικές εντολές | ⬜ | |
| 8 | Pink studio: 3 scripts, σκούπα pinkradio, φωνητικές εντολές με isolation | ⬜ | |
| 9 | Pipelines: local + Gemini, ελληνικό prompt με φιλικό ύφος, διαδικασία debug για το STT | ⬜ | |
| 10 | Shopping list: πολλαπλά items και ανάγνωση | ⬜ | |
| 11 | Reminders v2: recurring, πολλαπλοί χρόνοι ειδοποίησης, recipient, αλλαγή υπάρχοντος | ⬜ | |
| 12 | Satellite Σάρας (όταν έρθει) | ⬜ | |

## Ημερολόγιο

- 2026-10-11 — Βήμα 0 ξεκίνησε. Repo = ζωντανό config (`U:\homeassistant` ≡ `/volume1/docker/homeassistant`).
