# CLAUDE.md — Home Assistant config

Πηγή αλήθειας για το πώς δουλεύουμε σε αυτό το repo. Διαβάζεται πρώτο σε κάθε νέα συζήτηση,
μαζί με το `ROADMAP.md`. Όταν κάτι εδώ αλλάζει στην πράξη (rename, νέο entity), ενημερώνεται και αυτό το αρχείο.

## Περιβάλλον

- Home Assistant **Container** (`ghcr.io/home-assistant/home-assistant:stable`) σε Synology DS218+,
  `network_mode: host`, TZ `Europe/Athens` (βλ. `docker-compose.yml`). UI: `http://192.168.1.69:8123`.
- Config στο NAS: `/volume1/docker/homeassistant` → `/config` μέσα στο container.
- Στα Windows ο ίδιος φάκελος είναι mapped ως `U:\homeassistant`. **Δεν είναι ξεχωριστό clone.**
  Ό,τι γράφεται εκεί είναι αμέσως το ζωντανό config.
- Git repo μέσα στο config dir, private remote `spqqky/homeassistant-config`, branch `main`.
  - Synology: SSH key `id_ed25519` για το GitHub.
  - Windows / Fork: HTTPS remote (για να μη μπλέκουμε με το SSH key του Synology).
- Στο Git: `configuration.yaml`, `automations.yaml`, `scripts.yaml`, `scenes.yaml`, `custom_sentences/`,
  `docker-compose.yml`, και τα custom components `reminder_manager`, `xiaomi_miot`, `xiaomi_vac`, `mic_to_mediaplayer`.
  Εκτός Git (`.gitignore`): `.storage/`, `.cloud/`, `.cache/`, `tts/`, βάσεις, logs, `secrets.yaml`,
  `.HA_VERSION`, `.shopping_list.json`, `custom_components/hacs/`.
- Το `automations.yaml` και το `scripts.yaml` τα γράφει και το UI του HA. Πριν από κάθε αλλαγή με το χέρι
  ελέγχουμε το `git status` για αλλαγές που έγιναν από το UI και δεν έχουν γίνει commit.
- Δίκτυο: ενιαίο LAN με δύο segments (mesh στο σπίτι, δεύτερο router/AP για Pink Radio/υπόγειο).
  **Ένα** Home Assistant για όλα, όχι δύο installations.

## Κανόνες

1. **Βήμα-βήμα με τη σειρά του `ROADMAP.md`.** Δεν ανοίγουμε επόμενο βήμα πριν κλείσει το τρέχον.
   Όταν κλείνει ένα βήμα ενημερώνεται το `ROADMAP.md` (κατάσταση, ημερομηνία, commit).
2. **Δύο scopes / χώροι:** `home_*` (το σπίτι) και `pinkradio_*` (το studio, σε άλλο όροφο).
   Κάθε νέο entity, script ή automation ανήκει σε ένα από τα δύο και το όνομά του το δηλώνει.
3. **Isolation του Pink Radio:** από το Pink Assistant επιτρέπεται **μόνο** ο έλεγχος του studio.
   Κανένα `home_*` entity δεν γίνεται exposed ούτε ελέγχεται από εκεί, και τίποτα δεν ακούγεται στο σπίτι.
4. **Reusable scripts αντί για ένα automation ανά μικρή ενέργεια.** Τα voice automations απλώς καλούν scripts.
5. **Packages:** η λογική ζει στο `packages/<scope>/<λειτουργία>.yaml` (`core`, `home`, `pinkradio`, `shared`).
   Το `automations.yaml` / `scripts.yaml` κρατούν μόνο ό,τι φτιάχνεται από το UI. Επαναλαμβανόμενες φράσεις
   (δωμάτια, modes) γίνονται `lists` στο `custom_sentences/el/`, όχι αντιγραμμένα μπλοκ ανά δωμάτιο.
6. **Renames:** κάθε μετονομασία entity (στο UI) γίνεται **μαζί** με διόρθωση όλων των αναφορών στο YAML
   (grep σε `automations.yaml`, `scripts.yaml`, `packages/`, `custom_sentences/`) και στο ίδιο commit.
   Ποτέ rename μόνο στο UI, γιατί έτσι έσπασαν οι σκούπες.
7. **Git:** κάθε βήμα κλείνει με commit. Πριν από αλλαγές που δύσκολα αναιρούνται (renames, μαζικά edits YAML)
   γίνεται commit ή tag. Το tag `baseline` είναι η αρχική, ανέγγιχτη κατάσταση.
8. **Γραμμές YAML σε LF.** Το HA τρέχει σε Linux. Κανένα CRLF στα αρχεία YAML.
9. **Μετά από αλλαγή YAML:** έλεγχος config (Developer tools → YAML → Check configuration) και reload
   ή restart. Έλεγχος του `home-assistant.log` για errors.
10. Μυστικά μόνο στο `secrets.yaml` (ignored), με `!secret`.
11. Απαντήσεις και σχόλια στα ελληνικά. Τα ονόματα entities/scripts σε λατινικά, snake_case.

## Packages

`configuration.yaml` → `homeassistant: packages: !include_dir_named packages` (recursive, το όνομα αρχείου είναι το κλειδί,
άρα πρέπει να είναι μοναδικό). Μετά από αλλαγή στο `packages:` χρειάζεται **restart**, για τα υπόλοιπα αρκεί reload.

| Αρχείο | Περιεχόμενο |
|---|---|
| `packages/home/home_vacuum.yaml` | φωνητικά της σκούπας σπιτιού |
| `packages/home/home_announcements.yaml` | Voice - Ανακοινώσεις |
| `packages/home/home_media.yaml` | Music Assistant, Radio, scripts έντασης |
| `packages/pinkradio/pinkradio_studio.yaml` | Studio Control, Guitar Amp, scripts neon/audio/studio |
| `packages/pinkradio/pinkradio_led.yaml` | φωνητικά των LED, disco script |
| `packages/pinkradio/pinkradio_vacuum.yaml` | φωνητικά της σκούπας Pink |
| `packages/shared/shared_reminders.yaml` | reminders (scripts + notifications) |
| `packages/shared/shared_shopping.yaml` | shopping list scripts |

Το `automations.yaml` / `scripts.yaml` κρατούν μόνο ό,τι φτιάχνεται από το UI. Ό,τι φτιαχτεί εκεί μεταφέρεται στο σωστό package
στο επόμενο βήμα που αγγίζει τη λειτουργία.

## Δομή και naming convention

**Floors / areas** (βήμα 2):

| Floor | Area (εμφάνιση) | area_id | Aliases |
|---|---|---|---|
| `home` | Σαλόνι | `living_room` | σαλόνι, καθιστικό |
| `home` | Δωμάτιο Νεφέλης | `nefeli_room` | δωμάτιο της Νεφέλης, Νεφέλη |
| `home` | Δωμάτιο Αλεξάνδρας | `alex_room` | δωμάτιο της Αλεξάνδρας, Αλεξάνδρα |
| `home` | Κύρια κρεβατοκάμαρα | `bedroom` | κρεβατοκάμαρα, υπνοδωμάτιο, δωμάτιο της Σάρας |
| `pinkradio` | Pink Radio Studio | `pinkradio_studio` | Pink Radio, στούντιο, studio |
| `home` | Office | `office` | — (εκτυπωτής Brother, HACS) |

Το area_id / floor_id βγαίνει από το όνομα κατά τη δημιουργία και δεν αλλάζει μετά.

**Ονόματα:** με βάση το δωμάτιο και τον ρόλο, όχι τη μάρκα. Ο player του Music Assistant έχει το ίδιο όνομα με
`(MA)` στο device και `_ma` στο entity. Το Cast entity χρησιμοποιείται για TTS, το `_ma` για μουσική.

| Device name | Entity ID | Παλιό entity ID (πριν το βήμα 3) |
|---|---|---|
| Living Room Speaker | `media_player.home_living_room_speaker` | `media_player.jbl_nest` |
| Living Room Speaker (MA) | `media_player.home_living_room_speaker_ma` | `media_player.jbl_nest_music` |
| Nefeli Room Speaker | `media_player.home_nefeli_room_speaker` | `media_player.nefeli_room` |
| Nefeli Room Speaker (MA) | `media_player.home_nefeli_room_speaker_ma` | `media_player.nefeli_room_music` |
| Alex Room Speaker | `media_player.home_alex_room_speaker` | `media_player.alex_room` |
| Alex Room Speaker (MA) | `media_player.home_alex_room_speaker_ma` | `media_player.alex_room_music` |
| Bedroom Speaker | `media_player.home_bedroom_speaker` | `media_player.sarah_room` |
| Bedroom Speaker (MA) | `media_player.home_bedroom_speaker_ma` | `media_player.sarah_room_music` |
| Living Room Assistant | `assist_satellite.home_living_room_satellite` | `assist_satellite.home_satellite` |
| Nefeli Room Assistant | `assist_satellite.home_nefeli_room_satellite` | `assist_satellite.nefeli_satellite` |
| Alex Room Assistant | `assist_satellite.home_alex_room_satellite` | `assist_satellite.alex_satellite` |
| Pink Radio Studio Assistant | `assist_satellite.pinkradio_studio_satellite` | `assist_satellite.pink_satellite` |
| Studio KRK Left | `switch.pinkradio_krk_left` | `switch.pink_radio_plug1` |
| Studio Neon ON AIR | `switch.pinkradio_neon_onair` | `switch.pink_radio_plug2` |
| Studio Neon Anarchy | `switch.pinkradio_neon_anarchy` | `switch.pink_radio_plug3` |
| Studio Neon Thunder | `switch.pinkradio_neon_thunder` | `switch.pink_radio_plug4` |
| Studio Neon Pink Radio | `switch.pinkradio_neon_logo` | `switch.pink_radio_plug5` |
| Studio Onyx Console | `switch.pinkradio_onyx_console` | `switch.pink_radio_plug6` |
| Studio KRK Right | `switch.pinkradio_krk_right` | `switch.pink_radio_plug7` |
| Studio Guitar Amp | `switch.pinkradio_guitar_amp` | `switch.pink_radio_plug8` |
| Studio LED Main | `light.pinkradio_led_main` | `light.pink_radio_led_main` |
| Studio LED Drums | `light.pinkradio_led_drums` | `light.pink_radio_led_drums` |
| Home Vacuum | `vacuum.home_vacuum` | (ίδιο) |
| Pink Radio Vacuum | `vacuum.pinkradio_vacuum` | (ίδιο) |

Τα υπόλοιπα entities κάθε device ακολουθούν το πρόθεμά του (`select.home_living_room_assistant_wake_word`,
`sensor.pinkradio_neon_onair_power` κ.λπ.). Πλήρης λίστα: `docs/step3_entity_renames.csv`.
Μαζικές μετονομασίες: `tools/rename_entities.py <csv> [--apply]` (websocket API, κρατά ιστορικό).
Γέφυρες satellite → ηχείο (mic_to_mediaplayer): `sensor.home_<room>_assistant_bridge_pipeline_status`.

**Γνωστά προβλήματα integrations**
- `mic_to_mediaplayer` v1.5.3: διαβάζει μόνο τα `entry.data` και αγνοεί τα options. Για αλλαγή satellite ή ηχείου:
  **διαγραφή και επαναπροσθήκη** του entry, όχι Configure.
- Voice PE firmware **26.9.0**: crash κατά την αναπαραγωγή TTS (βλ. `docs/INVENTORY.md`). Ο Pink είναι σε **26.6.0**,
  με skip στο 26.9.0. Μην κάνεις update στα Voice PE χωρίς δοκιμή. Wake sound OFF στον Pink.
- STT: το pipeline «Home Assistant» (Pink) χρησιμοποιεί **Google AI STT**, γιατί το HA Cloud έκοβε λέξεις (π.χ. «στο»).
  Γνωστά: hallucinations, 503 σε ώρες αιχμής. Η σύγκριση γίνεται στο βήμα 9.
- Debug Voice PE: `tools/esphome_logs.py "<ESPHome entry>"` (WSL venv `~/ha-venv`, `aioesphomeapi`). Pipeline debug: Settings →
  Voice assistants → pipeline → ⋮ → Debug. Το κλειδί είναι τα events `stt-vad-start`/`stt-vad-end`.

## Πώς θέλω να λειτουργεί το Voice

### Assistants και satellites

4 ανεξάρτητοι assistants, ο καθένας σε συγκεκριμένο χώρο:

| Assistant | Satellite |
|---|---|
| Home Assistant / Home main | `assist_satellite.home_satellite` |
| Alex Assistant | `assist_satellite.alex_satellite` |
| Nefeli Assistant | `assist_satellite.nefeli_satellite` |
| Pink Assistant | `assist_satellite.pink_satellite` |

Πιθανός αργότερα: assistant για τη Σάρα.

**Βασική απαίτηση:** κάθε assistant ξέρει σε ποιο δωμάτιο βρίσκεται και απαντάει από το ηχείο **του δικού του**
δωματίου. Όχι απάντηση της Νεφέλης από το JBL του σαλονιού. Όχι ήχος στο σπίτι από εντολή στο Pink Radio.

Media players: `media_player.jbl_nest`, `media_player.nefeli_room`, `media_player.sarah_room`,
`media_player.alex_room`. **Δεν υπάρχει** media player για το Pink Radio.

### TTS

- `tts.google_translate_en_com` με `language: el` δουλεύει καλά για direct TTS σε Google Cast / Nest.
  Σε ορισμένα pipelines έχει χρησιμοποιηθεί και το Home Assistant Cloud TTS.
- Για ανακοινώσεις είναι πιο αξιόπιστο το explicit `tts.speak` από το να βασιζόμαστε στο output routing του Assist:

  ```yaml
  action: tts.speak
  target:
    entity_id: tts.google_translate_en_com
  data:
    media_player_entity_id: media_player.nefeli_room
    message: "..."
    language: el
  ```
- **Όχι διπλή εκφώνηση** (Assist response + external TTS).
- Στα local automations το `set_conversation_response` **δεν πρέπει να είναι κενό**. Το κενό response μπορεί
  να δώσει απαντήσεις τύπου «δεν μπόρεσα να το καταλάβω».

### STT

- `stt.google_ai_stt` σε `el-GR`.
- Έχει υπάρξει σοβαρό STT hallucination: το «σκούπισε το σαλόνι», ειπωμένο σε απόλυτη ησυχία, έγινε
  ολόκληρη άσχετη ελληνική παράγραφος.
- **Debug:** όταν ένα voice automation δεν ενεργοποιείται, ελέγχουμε κάθε στάδιο χωριστά και δεν θεωρούμε
  αυτόματα ότι φταίει το automation:

  ```
  Wake word → audio stream → STT → intent matching → automation → device action
  ```

### Home vacuum (Xiaomi S20+, `xiaomi.vacuum.b108gl`)

- Primary entity: `vacuum.home_vacuum`. Naming: `home_vacuum_*`.
- Entities:
  - `sensor.home_vacuum_battery_level`, `sensor.home_vacuum_status`
  - `button.home_vacuum_start_only_sweep`, `_start_sweep`, `_start_mop`, `_start_sweep_mop`,
    `_pause_sweeping`, `_continue_sweep`, `_start_charge`, `_stop_and_gocharge`
  - `select.home_vacuum_mode`, `_suction_level`, `_sweep_mop_type`, `_sweep_type`, `_mop_water_output_level`
- Room IDs:

  | ID | Δωμάτιο |
  |---|---|
  | 3 | Σαλόνι |
  | 4 | WC |
  | 5 | Hall |
  | 7 | Νεφέλη |
  | 8 | Κύρια κρεβατοκάμαρα |
  | 9 | Αλεξάνδρα |
  | 10 | Μπάνιο |

- Καθαρισμός δωματίου:

  ```yaml
  action: xiaomi_miot.call_action
  data:
    entity_id: vacuum.home_vacuum
    siid: 2
    aiid: 13
    params:
      - '{"room":[3]}'
  ```
- Fan speeds: `Silent`, `Basic`, `Strong`. **Default για κανονικό καθάρισμα: `Basic`.**

### Pink Radio vacuum (`xiaomi.vacuum.d106gl`)

- Primary entity: `vacuum.pinkradio_vacuum`. Naming: `pinkradio_vacuum_*`.
- Entities:
  - `sensor.pinkradio_vacuum_battery_level`, `_status`, `_cleaning_area`, `_cleaning_time`
  - `button.pinkradio_vacuum_start_only_sweep`, `_start_sweep`, `_start_mop`, `_start_sweep_mop`, `_stop`, `_start_charge`
  - `select.pinkradio_vacuum_mode`, `_suction_level`, `_sweep_type`
  - `number.pinkradio_vacuum_volume`, `switch.pinkradio_vacuum_alarm`
- Το Pink Assistant ελέγχει **αυτή** τη σκούπα όταν η εντολή αφορά «στούντιο» / «studio» / «Pink Radio»,
  ώστε να μην υπάρχει πιθανότητα να ξεκινήσει η home vacuum.

### Pink Radio studio

- LED: `light.pink_radio_led_main`, `light.pink_radio_led_drums` → θα γίνουν `light.pinkradio_*`.
- Shelly plugs (παλιά IDs): `switch.pink_radio_plug2` … `switch.pink_radio_plug7`.
  Λογική: plug1 KRK αριστερό, plug2 neon ON AIR, plug3 neon Anarchy, plug4 neon Thunder, plug5 neon Pink Radio, plug6 κονσόλα Onyx12, plug7 KRK δεξί, plug8 ενισχυτής κιθάρας.
  → θα πάρουν λειτουργικά ονόματα `pinkradio_*`.
- Υπάρχοντα scripts και τελικά ονόματα:

  | Τώρα | Τελικό | Παράμετρος |
  |---|---|---|
  | Pink Radio - Neon Control | `script.pinkradio_neon_control` | on/off |
  | Pink Radio - Studio Audio Control | `script.pinkradio_studio_audio_control` | on/off |
  | Pink Radio - Studio Control | `script.pinkradio_studio_control` | prepare/off |

### Reminders

- `calendar.reminders` + custom integration `reminder_manager`.
- Scripts: «Reminder - Create Chris», «Reminder - Find Chris», «Reminder - Delete Chris».
  Το Gemini τα χρησιμοποιεί για δημιουργία, αναζήτηση και διαγραφή.
- Automation στέλνει notification στο κινητό όταν φτάνει το calendar event.
- Μελλοντικά: recurring, πολλαπλοί χρόνοι ειδοποίησης, επιλογή recipient, αλλαγή υπάρχοντος,
  ίσως ξεχωριστό πραγματικό calendar.

### Shopping list

- `todo.shopping_list`. Scripts: «Shopping List - Add Items», «Shopping List - Read Items».
- Στόχος:
  - «βάλε γάλα ψωμί και τυρί στη λίστα» → προστίθενται και τα τρία.
  - «τι έχω στη λίστα για ψώνια;» → διαβάζει τη λίστα.
