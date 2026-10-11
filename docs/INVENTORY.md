# INVENTORY — κατάσταση στις 2026-10-11 (βήμα 1)

Στιγμιότυπο από τα `.storage/*` registries, το `automations.yaml`, το `scripts.yaml` και το `home-assistant.log`.
59 devices · 599 entities · 24 automations · 14 scripts · 5 pipelines · 49 exposed entities.

## 🔴 Ευρήματα που θέλουν προσοχή

1. **Τα automations των σκουπών είναι σπασμένα.** Τα entities μετονομάστηκαν σε `home_vacuum_*` / `pinkradio_vacuum_*`,
   αλλά το `automations.yaml` χρησιμοποιεί ακόμα τα παλιά IDs. Το log το επιβεβαιώνει σήμερα («Referenced entities … are missing»).

   | Παλιό ID (στο YAML) | Φορές | Νέο ID |
   |---|---|---|
   | `vacuum.saloni_skoupa_spitiou_marusca_robot_cleaner` | 155 | `vacuum.home_vacuum` |
   | `select.xiaomi_b108gl_fb61_mop_water_output_level` | 23 | `select.home_vacuum_mop_water_output_level` |
   | `button.xiaomi_b108gl_fb61_start_sweep_mop` | 2 | `button.home_vacuum_start_sweep_mop` |
   | `button.xiaomi_b108gl_fb61_continue_sweep` | 1 | `button.home_vacuum_continue_sweep` |
   | `select.saloni_skoupa_spitiou_marusca_robot_cleaner` | 1 | option `Level2`, μάλλον `select.home_vacuum_mop_water_output_level` |
   | `vacuum.pink_radio_skoupa_pink_robot_cleaner` | 12 | `vacuum.pinkradio_vacuum` |
   | `select.pink_radio_skoupa_pink_mode` | 2 | `select.pinkradio_vacuum_mode` |
   | `button.pink_radio_skoupa_pink_start_*` (3) | 3 | `button.pinkradio_vacuum_start_*` |
   | `media_player.alexandra_room` | 3 | `media_player.alex_room` |
   | `media_player.sarah_room_2` | 1 | μάλλον `media_player.sarah_room_music` (Music Assistant) |

   Επηρεάζονται 6 automations σκούπας σπιτιού, το «Voice - Pink Radio Σκούπα», το «Voice - Music Assistant»
   και το «Voice - Radio». Το `scripts.yaml` είναι καθαρό.
2. **Δεν υπάρχει isolation.** Υπάρχει μία κοινή λίστα exposed για όλους τους assistants. Το Pink βλέπει
   `vacuum.home_vacuum`, όλα τα media players του σπιτιού κ.λπ., και τα σπίτια βλέπουν τα plugs του studio.
3. **Το Pink Assistant δεν έχει δικό του pipeline.** Είναι στο `preferred` (= «Home Assistant», local agent).
4. **Το STT στην πράξη είναι `stt.home_assistant_cloud`** σε όλα τα pipelines, **όχι** `stt.google_ai_stt`
   (που υπάρχει αλλά δεν χρησιμοποιείται). Το log έχει σήμερα και `cloud.stt … 400 Invalid HTTP request`.
5. Το CLAUDE.md αναφέρει `media_player.alexandra_room`. Το πραγματικό entity είναι `media_player.alex_room`.
6. HACS: 4 repairs «restart required» σε εκκρεμότητα.
7. xiaomi_miot: η d106gl (Pink) δεν απαντά κατά διαστήματα («No response from the device 192.168.1.132»),
   και υπάρχουν deprecation warnings (wrong domain entity ID, deprecated constants μέχρι το 2027.8).

## Areas και floors

**Floors:** κανένα.

| area_id | Όνομα | Χρήση σήμερα |
|---|---|---|
| `saloni` | Σαλόνι | Home main, JBL, home vacuum, Gemini devices |
| `nefeli_room` | Nefeli Room | Nefeli Voice PE + Nest Audio |
| `alex_room` | Alex Room | Alex Voice PE + Nest Audio |
| `bedroom` | Bedroom | Sarah Room Nest Mini |
| `pink_radio` | Pink Radio | Pink Voice PE, plugs, LED, pink vacuum |
| `office` | Office | μόνο HACS |
| `living_room` | Living Room | κενό (διπλό του `saloni`) |
| `kitchen` | Kitchen | κενό |

Πολλά devices δεν έχουν area (TV, cast groups, Music Assistant players, Brother, κινητό).

## Satellites (όλα Nabu Casa Home Assistant Voice PE)

| Satellite | Device / ESPHome | Area | Assistant (pipeline) | Wake word | Έξοδος ήχου |
|---|---|---|---|---|---|
| `assist_satellite.home_satellite` | Home main / `0a8309` | saloni | Home Gemini | Okay Nabu | → `media_player.jbl_nest` (mic_to_mediaplayer) |
| `assist_satellite.alex_satellite` | Alex Assistant / `0ab189` | alex_room | Alex Gemini | Okay Nabu | → `media_player.alex_room` (mic_to_mediaplayer) |
| `assist_satellite.nefeli_satellite` | Nefeli assistant / `0a80c5` | nefeli_room | Nefeli Gemini | Okay Nabu | → `media_player.nefeli_room` (mic_to_mediaplayer) |
| `assist_satellite.pink_satellite` | Pink assistant / `0ad368` | pink_radio | preferred → «Home Assistant» | Okay Nabu | ηχείο του ίδιου του Voice PE |

Τα media players των ίδιων των Voice PE: `media_player.saloni_home_main_media_player`,
`media_player.home_assistant_voice_{0ab189,0a80c5,0ad368}_media_player` (ESPHome), καθώς και
`media_player.home_assistant_voice_{0a8309,0ab189,0a80c5,0ad368}` (Music Assistant).

## Pipelines

| Pipeline | Conversation | STT | TTS | prefer_local |
|---|---|---|---|---|
| Home Assistant (**preferred**) | `conversation.home_assistant` | HA Cloud el-GR | HA Cloud AthinaNeural | όχι |
| Home Assistant Cloud | `conversation.home_assistant` | HA Cloud | HA Cloud | όχι |
| Home Gemini | `conversation.home_gemini` | HA Cloud | HA Cloud | ναι |
| Alex Gemini | `conversation.alex_gemini` | HA Cloud | HA Cloud | ναι |
| Nefeli Gemini | `conversation.nefeli_gemini` | HA Cloud | HA Cloud | ναι |

Google Generative AI subentries: Common Assistant (`conversation.google_ai_conversation`, αχρησιμοποίητο),
Home / Alex / Nefeli Gemini (`gemini-3.1-flash-lite`), `stt.google_ai_stt`, `tts.google_ai_tts`, `ai_task.google_ai_task`.
TTS διαθέσιμα: `tts.google_translate_en_com`, `tts.home_assistant_cloud`, `tts.google_ai_tts`.

## Ηχεία / media players

| Φυσικό ηχείο | Cast entity | Music Assistant entity | Area |
|---|---|---|---|
| JBL Link Music (σαλόνι) | `media_player.jbl_nest` | `media_player.jbl_nest_music` | — |
| Nest Audio Νεφέλης | `media_player.nefeli_room` | `media_player.nefeli_room_music` | nefeli_room / — |
| Nest Audio Αλεξάνδρας | `media_player.alex_room` | `media_player.alex_room_music` | alex_room / — |
| Nest Mini Σάρας | `media_player.sarah_room` | `media_player.sarah_room_music` | bedroom / — |
| Cast group Kids | `media_player.kids` | `media_player.kids_2` | — |
| Cast group Οικιακή ομάδα | `media_player.oikiake_omada` | `media_player.oikiake_omada_2` | — |

Άλλα: TV (`lg_webos_tv_lr60006la`, `samsung_5_series_32`, `samsung_the_frame_32`, `tv_big_screen`), `xboxone`,
`a_box` / `a_box_2`. **Κανένα ηχείο στο Pink Radio** εκτός από το Voice PE.

## Σκούπες

| | Home | Pink Radio |
|---|---|---|
| Device | Σκούπα Σπιτιού, `xiaomi.vacuum.b108gl`, 192.168.1.142 | Σκούπα Pink, `xiaomi.vacuum.d106gl`, 192.168.1.132 (pink-net) |
| Primary | `vacuum.home_vacuum` (friendly «Marusca Robot Cleaner») | `vacuum.pinkradio_vacuum` |
| Area | saloni | pink_radio |
| Naming | ✅ `home_vacuum_*` | ✅ `pinkradio_vacuum_*` |

## Pink Radio studio

| Entity | Shelly device | Χρήση (από τα scripts) |
|---|---|---|
| `switch.pink_radio_plug1` | Plug M Gen3 «plug1» | ❓ άγνωστη (sensors: `shellyplugmg3_907069605588_*`) |
| `switch.pink_radio_plug2`–`plug5` | Plug M Gen3 | neon (`script.pink_radio_neon_control`) |
| `switch.pink_radio_plug6`, `plug7` | Plug S Gen3 | studio audio (`script.pink_radio_studio_audio_control`): κονσόλα Onyx12 / KRK; ❓ ποιο είναι ποιο |
| `switch.pink_radio_plug8` | Plug S Gen3 | ενισχυτής κιθάρας («Voice - Guitar Amp ON/OFF») |
| `light.pink_radio_led_main` | Plus RGBW PM «LED-main» | LED studio |
| `light.pink_radio_led_drums` | Plus RGBW PM «LED-drums» | LED drums |

Ασυνέπεια naming στα plugs: οι sensors/buttons/updates των plug1, plug4, plug5 είναι ακόμα `shellyplugmg3_<mac>_*`.

## Automations (24)

| Automation | Sentences | Στόχος | Σημείωση |
|---|---|---|---|
| Voice - Home Κανονικό σκούπισμα | 34 | home vacuum, TTS → jbl_nest | 🔴 παλιά IDs |
| Voice - Home Δυνατό σκούπισμα | 21 | home vacuum, TTS → jbl_nest | 🔴 |
| Voice - Home Ήσυχο σκούπισμα | 21 | home vacuum, TTS → jbl_nest | 🔴 |
| Voice - Home Σκούπισμα και σφουγγάρισμα | 21 | home vacuum, TTS → jbl_nest | 🔴 |
| Voice - Home Πολύ νερό | 27 | home vacuum, TTS → jbl_nest | 🔴 |
| Voice - Home Έλεγχος και κατάσταση σκούπας | 23 | home vacuum, TTS → jbl_nest | 🔴 |
| Voice - Ανακοινώσεις | 46 | `tts.speak` (HA Cloud) → nefeli/alex/sarah/jbl | mode queued |
| Voice - Music Assistant | 21 | `music_assistant.play_media` | 🔴 `alexandra_room` |
| Voice - Radio | 67 | `music_assistant.play_media` | 🔴 `alexandra_room`, `sarah_room_2` |
| Reminders - Chris Notifications | — (calendar trigger) | `notify.chris_smartphone` | |
| Voice - Guitar Amp ON/OFF | 28 | plug8 | |
| Voice - LED ON/OFF Studio | 14 | led_main | |
| Voice - LED Colors Studio | 5 | led_main | |
| Voice - Studio LED Modes | 9 | led_main | |
| Voice - LED Brightness Studio | 4 | led_main | χωρίς `set_conversation_response` |
| Voice - LED Brightness Up/Down Studio | 8 | led_main | χωρίς response |
| Voice - Studio Disco Mode | 15 | `script.studio_led_disco_mode` | χωρίς response |
| Voice - LED Brightness Drums | 4 | led_drums | χωρίς response |
| Voice - LED Brightness Up/Down Drums | 8 | led_drums | χωρίς response |
| Voice - LED ON/OFF drums (`automation.new_automation`) | 14 | led_drums | κακό entity_id |
| Voice - LED ON/OFF (`automation.led_on_off`) | 14 | led_main + led_drums | χωρίς «στούντιο» στις φράσεις |
| Voice - LED Colour Drums | 10 | led_drums | |
| Voice - Pink Radio Σκούπα | 66 | pink vacuum | 🔴 παλιά IDs |
| Voice - Pink Radio Studio Control | 75 | τα 3 scripts του Pink Radio | |

Κανένα voice automation δεν φιλτράρει ανά satellite (`trigger.device_id` / `satellite_id`): όλα ενεργοποιούνται από οποιονδήποτε assistant.

## Scripts (14)

| Script | Fields | Exposed |
|---|---|---|
| `reminder_create_chris` / `_find_chris` / `_delete_chris` | text, datetime, minutes_before / search | ✅ |
| `voice_pe_volume_control` (Home main PE) | volume_percent | ✅ |
| `jbl_volume_control` | volume_percent | ✅ |
| `nefeli_nest_volume_control` | volume_percent | ✅ |
| `sarah_nest_volume_control` | volume_percent | ✅ |
| `shopping_list_add_items` | products | ❌ |
| `shopping_list_read_items` | — | ❌ |
| `studio_led_disco_mode` | — | ❌ |
| `pink_radio_neon_control` | action on/off | ❌ |
| `pink_radio_studio_audio_control` | action on/off | ❌ |
| `pink_radio_studio_control` | studio_action prepare/off | ❌ |

## Exposed entities (49, κοινά για όλους τους assistants)

- media_player: 27 (όλα, μαζί με TV, Xbox, τα διπλά των Music Assistant και τα media players των Voice PE)
- switch: `pink_radio_plug1`–`plug8`, `pinkradio_vacuum_alarm`, `home_vacuum_physical_control_locked`
- light: `pink_radio_led_main`, `pink_radio_led_drums`
- vacuum: `home_vacuum`, `pinkradio_vacuum`
- script: 7 (reminders + volume)
- todo: `shopping_list`

## Custom components / sentences

- `custom_components/`: `reminder_manager`, `xiaomi_miot`, `xiaomi_vac`, `mic_to_mediaplayer`, `hacs` (ignored).
- `custom_sentences/el/announcements.yaml`: wildcard lists `message`, `song`, `station`, plus `month`, `before` κ.λπ.
- `blueprints/`: μόνο τα default (motion_light, notify_leaving_zone, confirmable_notification).

## Ανοιχτές ερωτήσεις (για τον χρήστη)

1. `switch.pink_radio_plug1`: τι είναι συνδεδεμένο;
2. `plug6` / `plug7`: ποιο είναι η κονσόλα Onyx12 και ποιο τα KRK;
3. `plug2`–`plug5`: όλα neon ή κάποιο είναι «άλλος εξοπλισμός studio»;
4. Pink Radio: θα μπει ηχείο, ή το Voice PE μένει η μόνη έξοδος;
5. Η Σάρα είναι στην «Κύρια κρεβατοκάμαρα» (area `bedroom`) ή σε δικό της δωμάτιο;
