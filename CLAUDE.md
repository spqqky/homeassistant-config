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
5. **Git:** κάθε βήμα κλείνει με commit. Πριν από αλλαγές που δύσκολα αναιρούνται (renames, μαζικά edits YAML)
   γίνεται commit ή tag. Το tag `baseline` είναι η αρχική, ανέγγιχτη κατάσταση.
6. **Γραμμές YAML σε LF.** Το HA τρέχει σε Linux. Κανένα CRLF στα αρχεία YAML.
7. **Μετά από αλλαγή YAML:** έλεγχος config (Developer tools → YAML → Check configuration) και reload
   ή restart. Έλεγχος του `home-assistant.log` για errors.
8. Μυστικά μόνο στο `secrets.yaml` (ignored), με `!secret`.
9. Απαντήσεις και σχόλια στα ελληνικά. Τα ονόματα entities/scripts σε λατινικά, snake_case.

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
`media_player.alexandra_room`. **Δεν υπάρχει** media player για το Pink Radio.

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
  Λογική: neon lights, console / Onyx12, KRK speakers, άλλος εξοπλισμός studio.
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
