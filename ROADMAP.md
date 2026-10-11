# ROADMAP

Κατάσταση: ⬜ εκκρεμεί · 🔄 σε εξέλιξη · ✅ ολοκληρώθηκε

| # | Βήμα | Κατάσταση | Σημειώσεις |
|---|------|-----------|------------|
| 0 | Workspace: σύνδεση φακέλου, CLAUDE.md, ROADMAP.md, git tag `baseline` | ✅ | commit `1e9637a`, tag `baseline` → `a67485b` |
| 1 | Inventory: entities, satellites (hardware, έξοδος ήχου), pipelines, automations, scripts | ✅ | `docs/INVENTORY.md` (`bd689bc`). Hotfix IDs: `53b3907` |
| 2 | Δομή: floors `home` / `pinkradio`, areas, satellites στα areas τους | ✅ | floors home/pinkradio, areas `living_room`, `nefeli_room`, `alex_room`, `bedroom`, `office`, `pinkradio_studio`· device names κατά το convention· MA players TV/Xbox/a-box/Voice PE απενεργοποιημένοι |
| 2β | Οργάνωση αρχείων: `packages/` ανά scope/λειτουργία (`core`, `home`, `pinkradio`, `shared`), `custom_sentences` με lists αντί για copy-paste ανά δωμάτιο. Το `automations.yaml` κρατά μόνο ό,τι φτιάχνεται από το UI | 🔄 | |
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
- 2026-10-11 — Βήμα 1: inventory στο `docs/INVENTORY.md`. Βρέθηκαν σπασμένα automations σκούπας (παλιά entity IDs).
- 2026-10-11 — Hotfix: αντικατάσταση παλιών entity IDs στο `automations.yaml` (203 γραμμές: σκούπες, `alex_room`, `sarah_room`). Προσωρινό μέχρι τα βήματα 7/8.
- 2026-10-11 — Απόφαση: δομή με packages (νέο βήμα 2β). Ό,τι είναι σε package επεξεργάζεται από το αρχείο, όχι από το UI.
- 2026-10-11 — Βήμα 1 ολοκληρώθηκε. Pink Radio χωρίς ηχείο (έξοδος = Voice PE). Η Σάρα στην κύρια κρεβατοκάμαρα.
- 2026-10-11 — Βήμα 2 ολοκληρώθηκε. Οι αλλαγές floors/areas/device names είναι στο `.storage` (εκτός git)· η τεκμηρίωση στο CLAUDE.md «Δομή και naming convention».
