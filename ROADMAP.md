# ROADMAP

Κατάσταση: ⬜ εκκρεμεί · 🔄 σε εξέλιξη · ✅ ολοκληρώθηκε

| # | Βήμα | Κατάσταση | Σημειώσεις |
|---|------|-----------|------------|
| 0 | Workspace: σύνδεση φακέλου, CLAUDE.md, ROADMAP.md, git tag `baseline` | ✅ | commit `1e9637a`, tag `baseline` → `a67485b` |
| 1 | Inventory: entities, satellites (hardware, έξοδος ήχου), pipelines, automations, scripts | ✅ | `docs/INVENTORY.md` (`bd689bc`). Hotfix IDs: `53b3907` |
| 2 | Δομή: floors `home` / `pinkradio`, areas, satellites στα areas τους | ✅ | floors home/pinkradio, areas `living_room`, `nefeli_room`, `alex_room`, `bedroom`, `office`, `pinkradio_studio`· device names κατά το convention· MA players TV/Xbox/a-box/Voice PE απενεργοποιημένοι |
| 2β | Οργάνωση αρχείων: `packages/` ανά scope/λειτουργία (`core`, `home`, `pinkradio`, `shared`), `custom_sentences` με lists αντί για copy-paste ανά δωμάτιο. Το `automations.yaml` κρατά μόνο ό,τι φτιάχνεται από το UI | ✅ | 8 packages (`home`, `pinkradio`, `shared`), 24 automations + 13 scripts αυτούσια, ίδια ids. Τα lists στα `custom_sentences` γίνονται στα βήματα 7/8 |
| 3 | Naming cleanup: `pink_radio_*` → `pinkradio_*`, plugs με λειτουργικά ονόματα, grep και διόρθωση σε όλο το YAML | ✅ | 278 entities (`docs/step3_*.csv`), YAML 175 αντικαταστάσεις, γέφυρες ξαναστήθηκαν. Εκκρεμεί: prompt Home Gemini (`docs/prompts/`) |
| 4 | Μοντέλο ασφαλείας: exposed entities, pipeline του Pink, guards (και MCP, αν το θέλουμε) | ✅ | exposure 50→12 (`config/assist_exposed.txt`), guards σε 23 automations, pipeline «Pink Radio» τοπικό. MCP: όχι. Εκκρεμεί δοκιμή από Νεφέλη/σαλόνι |
| 5 | Voice routing core: `script.voice_speak`, default έξοδος ανά assistant | ✅ | `packages/core/core_voice.yaml`, κανόνας «απάντηση = μόνο set_conversation_response». Δοκιμή studio ✅, εκκρεμεί σαλόνι |
| 6 | Ανακοινώσεις: refactor του «Voice - Ανακοινώσεις» | ✅ | 1 automation / 6 triggers μέσω `voice_speak`. Διορθώθηκαν το «πες στον Χρήστο» (bug `tell_δαδ`) και η κενή απάντηση |
| 7 | Home vacuum: ανά δωμάτιο, Basic default, φωνητικές εντολές | ✅ | `script.home_vacuum_clean` + «Voice Clean» (ανά δωμάτιο, δυνατά/ήσυχα/σφουγγάρισμα). Εκκρεμεί πραγματικός καθαρισμός από το σπίτι |
| 8 | Pink studio: 3 scripts, σκούπα pinkradio, φωνητικές εντολές με isolation | ✅ | 8α διακόπτες (`pinkradio_voice_studio`), 8β LED (11 → 1 automation), 8γ `shared_vacuum.yaml`: «η σκούπα» = σκούπα του χώρου. Δοκιμές από τον Pink ✅ |
| 9 | Pipelines: local + Gemini, ελληνικό prompt με φιλικό ύφος, διαδικασία debug για το STT | ⬜ | |
| 10 | Shopping list: πολλαπλά items και ανάγνωση | ⬜ | |
| 11 | Reminders v2: recurring, πολλαπλοί χρόνοι ειδοποίησης, recipient, αλλαγή υπάρχοντος | ⬜ | |
| 12 | Dashboards: νέα dashboards για `home` και `pinkradio` (το παλιό Pink Radio έχει σπασμένες κάρτες· γρήγορη διόρθωση: `docs/lovelace_pink_radio.yaml`) | ⬜ | |
| 13 | Satellite Σάρας (όταν έρθει) | ⬜ | |

## Ημερολόγιο

- 2026-10-11 — Βήμα 0 ξεκίνησε. Repo = ζωντανό config (`U:\homeassistant` ≡ `/volume1/docker/homeassistant`).
- 2026-10-11 — Βήμα 1: inventory στο `docs/INVENTORY.md`. Βρέθηκαν σπασμένα automations σκούπας (παλιά entity IDs).
- 2026-10-11 — Hotfix: αντικατάσταση παλιών entity IDs στο `automations.yaml` (203 γραμμές: σκούπες, `alex_room`, `sarah_room`). Προσωρινό μέχρι τα βήματα 7/8.
- 2026-10-11 — Απόφαση: δομή με packages (νέο βήμα 2β). Ό,τι είναι σε package επεξεργάζεται από το αρχείο, όχι από το UI.
- 2026-10-11 — Βήμα 1 ολοκληρώθηκε. Pink Radio χωρίς ηχείο (έξοδος = Voice PE). Η Σάρα στην κύρια κρεβατοκάμαρα.
- 2026-10-11 — Βήμα 2 ολοκληρώθηκε. Οι αλλαγές floors/areas/device names είναι στο `.storage` (εκτός git)· η τεκμηρίωση στο CLAUDE.md «Δομή και naming convention».
- 2026-10-11 — Απόφαση: το βήμα 3 γίνεται πριν από το 2β, ώστε τα packages να γραφτούν κατευθείαν με τα τελικά IDs.
- 2026-10-11 — Βήμα 3 ολοκληρώθηκε. Bug στο mic_to_mediaplayer (αγνοεί options): οι 3 γέφυρες ξαναστήθηκαν. Η γέφυρα του σαλονιού δεν δούλευε ούτε πριν. Νέο βήμα 12: dashboards.
- 2026-10-11 — Pink Voice PE: downgrade σε 26.6.0 (crash στο 26.9.0). plug1 = KRK αριστερό, plug7 = KRK δεξί. Νέο dashboard Pink Radio (`docs/lovelace_pink_radio.yaml`).
- 2026-10-11 — Βήμα 2β ολοκληρώθηκε. `homeassistant: packages: !include_dir_named packages`. Pipeline «Home Assistant»: STT → Google AI STT (επιλογή χρήστη, το HA Cloud έκοβε λέξεις).
- 2026-10-11 — Βήμα 4 ολοκληρώθηκε. Studio: Pink + σαλόνι. Σπίτι: μόνο floor home. Δοκιμή από τον Pink ✅ (studio εκτελείται, σπίτι απορρίπτεται).
- 2026-10-11 — Βήμα 5 ολοκληρώθηκε. Το `voice_speak` δεν χρησιμοποιείται ακόμα. Συνδέεται στα βήματα 6 (ανακοινώσεις) και 7 (σκούπα, διπλή εκφώνηση).
- 2026-10-11 — Βήμα 6 ολοκληρώθηκε. Οι λίστες του custom_sentences δεν λειτουργούν στα triggers: παραλλαγές inline. `voice_speak` → HA Cloud TTS (Athina).
- 2026-10-11 — 8α ολοκληρώθηκε: «Pink Radio - Voice Studio» αντικαθιστά τα Studio Control / Guitar Amp. «τον ήχο» θέλει «στο στούντιο». Δοκιμή από τον Pink ✅. Google AI STT: ένα `stt-stream-failed` (πιθανό όριο Gemini), βλ. βήμα 9.
- 2026-10-11 — Βήματα 7 και 8 ολοκληρώθηκαν. LED: χωρίς προσδιορισμό → και τα δύο σετ. Σκούπες: κοινό «Vacuum - Voice Control», επιλογή ανά χώρο, Pink ✅ (studio εκτελείται, σπίτι απορρίπτεται).
