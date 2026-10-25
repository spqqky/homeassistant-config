"""Reminder Manager v2 για το Home Assistant (βήμα 11).

Υπενθυμίσεις στο calendar.reminders. Κάθε υπενθύμιση («ομάδα», με κοινό id) είναι ένα ή περισσότερα events,
ένα ανά ώρα ειδοποίησης (π.χ. 1 μέρα πριν + 1 ώρα πριν). Το event ξεκινά τη στιγμή της ειδοποίησης.
Η περιγραφή κρατά τα στοιχεία της υπενθύμισης:

    Ραντεβού/γεγονός: 18/05/2027 10:00 | για: chris,nefeli | πριν: 60 | επανάληψη: weekly | id: 3f9a1c2b

Παλιά events (v1, χωρίς «για»/«id») διαβάζονται κανονικά: παραλήπτης chris, id = το uid του event.

Services (όλα επιστρέφουν response):
    reminder_manager.create_reminder   text, event_datetime, before[], recipients[], repeat, days[]
    reminder_manager.find_reminders    search_text, event_date
    reminder_manager.update_reminder   search_text, event_date, new_*
    reminder_manager.delete_reminder   search_text, event_date
"""

from __future__ import annotations

from datetime import datetime, timedelta
import logging
import re
import unicodedata
import uuid

import voluptuous as vol

from homeassistant.components.calendar import CalendarEntityFeature
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.exceptions import HomeAssistantError
from homeassistant.util import dt as dt_util

DOMAIN = "reminder_manager"
CALENDAR = "calendar.reminders"
SEARCH_DAYS = 730

_LOGGER = logging.getLogger(__name__)

RECIPIENTS = ["chris", "nefeli", "alex"]
REPEATS = {
    "none": None,
    "daily": "FREQ=DAILY",
    "weekly": "FREQ=WEEKLY",
    "weekdays": "FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR",
    "monthly": "FREQ=MONTHLY",
    "yearly": "FREQ=YEARLY",
}
DAY_CODES = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]

RE_EVENT = re.compile(r"Ραντεβού/γεγονός:\s*(\d{2}/\d{2}/\d{4})(?:\s+(\d{1,2}:\d{2}))?")
RE_FOR = re.compile(r"για:\s*([a-z,\s]+)")
RE_BEFORE = re.compile(r"πριν:\s*(\d+)")
RE_BEFORE_V1 = re.compile(r"Υπενθύμιση\s+(\d+)\s+λεπτά πριν")
RE_REPEAT = re.compile(r"επανάληψη:\s*([a-z]+)")
RE_DAYS = re.compile(r"μέρες:\s*([A-Z,]+)")
RE_ID = re.compile(r"id:\s*([0-9a-f]{8})")


# ── Βοηθητικά ──────────────────────────────────────────────────────────────────────────────

def normalize(value: str) -> str:
    """Πεζά, χωρίς τόνους (για αναζήτηση)."""
    value = unicodedata.normalize("NFD", (value or "").casefold())
    return "".join(c for c in value if unicodedata.category(c) != "Mn")


def as_list(value, default):
    """Δέχεται λίστα ή κείμενο με κόμματα. Κενό → default."""
    if value is None or value == "" or value == []:
        return list(default)
    if isinstance(value, (int, float)):
        return [value]
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, str):
        return [v.strip() for v in value.split(",") if v.strip()]
    return list(value)


def parse_dt(hass: HomeAssistant, value: str) -> datetime:
    """«YYYY-MM-DD HH:MM[:SS]» σε ώρα Ελλάδας (ή της ρύθμισης του HA)."""
    value = value.strip().replace("T", " ")
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            naive = datetime.strptime(value, fmt)
            return naive.replace(tzinfo=dt_util.get_time_zone(hass.config.time_zone))
        except ValueError:
            continue
    raise ValueError("Η ημερομηνία πρέπει να είναι YYYY-MM-DD HH:MM.")


def shift_days(days: list[str], delta_days: int) -> list[str]:
    """Μετακινεί τις μέρες εβδομάδας (BYDAY) όταν η ειδοποίηση πέφτει άλλη μέρα από το γεγονός."""
    return [DAY_CODES[(DAY_CODES.index(d) - delta_days) % 7] for d in days]


def build_rrule(repeat: str, days: list[str], event_dt: datetime, notify_dt: datetime, until: str | None) -> str | None:
    base = REPEATS.get(repeat or "none")
    if base is None:
        return None
    delta = (event_dt.date() - notify_dt.date()).days
    if repeat == "weekly" and days:
        base = "FREQ=WEEKLY;BYDAY=" + ",".join(shift_days(days, delta))
    elif "BYDAY=" in base and delta:
        head, byday = base.split("BYDAY=")
        base = head + "BYDAY=" + ",".join(shift_days(byday.split(","), delta))
    if until:
        base += ";UNTIL=" + until.replace("-", "") + "T235959"
    return base


def get_calendar(hass: HomeAssistant):
    component = hass.data.get("calendar")
    if component is None:
        raise HomeAssistantError("Το calendar integration δεν είναι διαθέσιμο.")
    entity = component.get_entity(CALENDAR)
    if entity is None:
        raise HomeAssistantError("Δεν βρέθηκε το calendar.reminders.")
    return entity


def ev_start(event) -> datetime:
    s = event.start
    if isinstance(s, datetime):
        return dt_util.as_local(s)
    return dt_util.start_of_local_day(s)


def parse_event(event) -> dict:
    """Στοιχεία υπενθύμισης από ένα calendar event (v2 ή v1)."""
    desc = event.description or ""
    start = ev_start(event)
    m = RE_BEFORE.search(desc) or RE_BEFORE_V1.search(desc)
    before = int(m.group(1)) if m else 0
    appointment = start + timedelta(minutes=before)  # για επαναλαμβανόμενα: η πραγματική εμφάνιση
    m = RE_FOR.search(desc)
    recipients = [r.strip() for r in m.group(1).split(",") if r.strip()] if m else ["chris"]
    m = RE_REPEAT.search(desc)
    repeat = m.group(1) if m else ("custom" if event.rrule else "none")
    m = RE_DAYS.search(desc)
    days = m.group(1).split(",") if m else []
    m = RE_ID.search(desc)
    gid = m.group(1) if m else (event.uid or "")
    return {
        "id": gid,
        "uid": event.uid,
        "summary": event.summary,
        "appointment": appointment,
        "before": before,
        "recipients": recipients,
        "repeat": repeat,
        "days": days,
        "notification": start,
        "recurring": bool(event.rrule or event.recurrence_id),
    }


def group_events(events) -> list[dict]:
    """Ομαδοποίηση ανά id. Για επαναλαμβανόμενες κρατάμε την επόμενη εμφάνιση."""
    groups: dict[str, dict] = {}
    for ev in events:
        p = parse_event(ev)
        g = groups.setdefault(p["id"], {
            "id": p["id"], "summary": p["summary"], "appointment": p["appointment"],
            "recipients": p["recipients"], "repeat": p["repeat"], "days": p["days"],
            "before": set(), "uids": set(), "next_notification": p["notification"],
        })
        g["before"].add(p["before"])
        g["uids"].add(p["uid"])
        if p["appointment"] < g["appointment"]:
            g["appointment"] = p["appointment"]
        if p["notification"] < g["next_notification"]:
            g["next_notification"] = p["notification"]
    return sorted(groups.values(), key=lambda g: g["appointment"])


def public(g: dict) -> dict:
    """Ό,τι επιστρέφεται στο LLM / στα scripts."""
    return {
        "id": g["id"],
        "text": g["summary"],
        "event_datetime": g["appointment"].strftime("%Y-%m-%d %H:%M"),
        "event_date": g["appointment"].date().isoformat(),
        "minutes_before": sorted(g["before"], reverse=True),
        "recipients": g["recipients"],
        "repeat": g["repeat"],
        "days": g["days"],
    }


async def all_events(hass: HomeAssistant, entity):
    start = dt_util.now()
    return await entity.async_get_events(hass, start, start + timedelta(days=SEARCH_DAYS))


def matching(groups: list[dict], search_text: str, event_date: str) -> list[dict]:
    q = normalize(search_text)
    out = []
    for g in groups:
        if q and q not in normalize(g["summary"]):
            continue
        if event_date and g["appointment"].date().isoformat() != event_date:
            continue
        out.append(g)
    return out


async def create_group(hass, entity, text, event_dt, befores, recipients, repeat, days, until, gid=None) -> dict:
    gid = gid or uuid.uuid4().hex[:8]
    # Η πρώτη εμφάνιση πρέπει να πέφτει σε μέρα του κανόνα (αλλιώς κάποια calendars τη μετρούν ως έξτρα εμφάνιση)
    allowed = days if (repeat == "weekly" and days) else (DAY_CODES[:5] if repeat == "weekdays" else None)
    if allowed:
        while DAY_CODES[event_dt.weekday()] not in allowed:
            event_dt += timedelta(days=1)
    created = []
    for b in sorted({int(x) for x in befores}, reverse=True):
        notify_dt = event_dt - timedelta(minutes=b)
        rrule = build_rrule(repeat, days, event_dt, notify_dt, until)
        if rrule is None and notify_dt <= dt_util.now():
            continue  # μη επαναλαμβανόμενη ειδοποίηση στο παρελθόν: παραλείπεται
        desc = (f"Ραντεβού/γεγονός: {event_dt:%d/%m/%Y %H:%M} | για: {','.join(recipients)} | πριν: {b}"
                f" | επανάληψη: {repeat or 'none'}" + (f" | μέρες: {','.join(days)}" if days else "") + f" | id: {gid}")
        data = {"summary": text, "description": desc, "dtstart": notify_dt, "dtend": notify_dt + timedelta(minutes=1)}
        if rrule:
            data["rrule"] = rrule
        await entity.async_create_event(**data)
        created.append(b)
    return {"id": gid, "first_event_datetime": event_dt.strftime("%Y-%m-%d %H:%M"), "created_minutes_before": created}


async def delete_group(entity, g: dict) -> None:
    for uid in g["uids"]:
        if uid:
            await entity.async_delete_event(uid)  # χωρίς recurrence_id: σβήνει όλη τη σειρά


def validate_common(recipients, repeat, days):
    bad = [r for r in recipients if r not in RECIPIENTS]
    if bad:
        return f"Άγνωστος παραλήπτης: {', '.join(bad)}. Επιτρέπονται: {', '.join(RECIPIENTS)}."
    if repeat not in REPEATS:
        return f"Άγνωστη επανάληψη: {repeat}. Επιτρέπονται: {', '.join(REPEATS)}."
    bad = [d for d in days if d not in DAY_CODES]
    if bad:
        return f"Άγνωστη μέρα: {', '.join(bad)}. Επιτρέπονται: {', '.join(DAY_CODES)}."
    return None


# ── Services ──────────────────────────────────────────────────────────────────────────────

async def async_setup(hass: HomeAssistant, config: dict) -> bool:

    def check_features(entity, feature):
        if not (entity.supported_features and entity.supported_features & feature):
            raise HomeAssistantError("Το ημερολόγιο δεν υποστηρίζει αυτή την ενέργεια.")

    async def create_reminder(call: ServiceCall) -> dict:
        try:
            entity = get_calendar(hass)
            check_features(entity, CalendarEntityFeature.CREATE_EVENT)
            event_dt = parse_dt(hass, call.data["event_datetime"])
            befores = [int(x) for x in as_list(call.data.get("before"), [0])]
            recipients = [r.lower() for r in as_list(call.data.get("recipients"), ["chris"])]
            repeat = call.data.get("repeat") or "none"
            days = [d.upper() for d in as_list(call.data.get("days"), [])]
            err = validate_common(recipients, repeat, days)
            if err:
                return {"status": "invalid", "message": err}
            if repeat == "none" and event_dt <= dt_util.now():
                return {"status": "invalid", "message": "Η ώρα του γεγονότος έχει ήδη περάσει."}
            res = await create_group(hass, entity, call.data["text"].strip(), event_dt, befores, recipients,
                                     repeat, days, call.data.get("until") or None)
            if not res["created_minutes_before"]:
                return {"status": "invalid", "message": "Όλες οι ώρες ειδοποίησης έχουν ήδη περάσει."}
            return {"status": "created", "text": call.data["text"].strip(),
                    "event_datetime": event_dt.strftime("%Y-%m-%d %H:%M"), "recipients": recipients,
                    "repeat": repeat, "days": days, **res}
        except (HomeAssistantError, ValueError) as err:
            _LOGGER.exception("Reminder create failed")
            return {"status": "error", "message": str(err)}

    async def find_reminders(call: ServiceCall) -> dict:
        try:
            entity = get_calendar(hass)
            groups = group_events(await all_events(hass, entity))
            found = matching(groups, call.data.get("search_text", ""), call.data.get("event_date", ""))
            return {"status": "ok", "count": len(found), "reminders": [public(g) for g in found[:30]]}
        except (HomeAssistantError, ValueError) as err:
            _LOGGER.exception("Reminder find failed")
            return {"status": "error", "message": str(err)}

    async def pick_one(call: ServiceCall):
        """Βρίσκει ΜΙΑ υπενθύμιση ή επιστρέφει (None, response σφάλματος)."""
        search_text = call.data.get("search_text", "").strip()
        event_date = call.data.get("event_date", "").strip()
        if len(search_text) < 3:
            return None, None, {"status": "invalid", "message": "Χρειάζονται τουλάχιστον τρεις χαρακτήρες αναζήτησης."}
        if event_date:
            try:
                event_date = datetime.strptime(event_date, "%Y-%m-%d").date().isoformat()
            except ValueError:
                return None, None, {"status": "invalid", "message": "Η ημερομηνία πρέπει να είναι YYYY-MM-DD."}
        entity = get_calendar(hass)
        found = matching(group_events(await all_events(hass, entity)), search_text, event_date)
        if not found:
            return None, None, {"status": "not_found", "message": "Δεν βρέθηκε υπενθύμιση με αυτά τα στοιχεία.",
                                "search_text": search_text, "event_date": event_date}
        if len(found) > 1:
            return None, None, {"status": "multiple_matches",
                                "message": "Βρέθηκαν περισσότερες από μία υπενθυμίσεις. Χρειάζεται διευκρίνιση.",
                                "reminders": [public(g) for g in found[:20]]}
        return entity, found[0], None

    async def delete_reminder(call: ServiceCall) -> dict:
        try:
            entity, g, err = await pick_one(call)
            if err:
                return err
            check_features(entity, CalendarEntityFeature.DELETE_EVENT)
            await delete_group(entity, g)
            return {"status": "deleted", **public(g), "message": "Η υπενθύμιση διαγράφηκε."}
        except (HomeAssistantError, ValueError) as err:
            _LOGGER.exception("Reminder delete failed")
            return {"status": "error", "message": str(err)}

    async def update_reminder(call: ServiceCall) -> dict:
        try:
            entity, g, err = await pick_one(call)
            if err:
                return err
            check_features(entity, CalendarEntityFeature.CREATE_EVENT)
            check_features(entity, CalendarEntityFeature.DELETE_EVENT)
            old = public(g)
            text = (call.data.get("new_text") or "").strip() or g["summary"]
            new_dt = call.data.get("new_event_datetime")
            event_dt = parse_dt(hass, new_dt) if new_dt else g["appointment"]
            befores = [int(x) for x in as_list(call.data.get("new_before"), sorted(g["before"]))]
            recipients = [r.lower() for r in as_list(call.data.get("new_recipients"), g["recipients"])]
            repeat = call.data.get("new_repeat") or (g["repeat"] if g["repeat"] in REPEATS else "none")
            days = [d.upper() for d in as_list(call.data.get("new_days"), g["days"])]
            err = validate_common(recipients, repeat, days)
            if err:
                return {"status": "invalid", "message": err}
            if repeat == "none" and event_dt <= dt_util.now():
                return {"status": "invalid", "message": "Η νέα ώρα έχει ήδη περάσει."}
            await delete_group(entity, g)
            res = await create_group(hass, entity, text, event_dt, befores, recipients, repeat, days, None, gid=g["id"])
            return {"status": "updated", "before_change": old, "text": text,
                    "event_datetime": event_dt.strftime("%Y-%m-%d %H:%M"), "recipients": recipients,
                    "repeat": repeat, "days": days, **res}
        except (HomeAssistantError, ValueError) as err:
            _LOGGER.exception("Reminder update failed")
            return {"status": "error", "message": str(err)}

    list_or_str = vol.Any(str, list, tuple, int, float)  # «1440,60», [1440, 60], 60 (τα templates του HA δίνουν και tuple)

    hass.services.async_register(DOMAIN, "create_reminder", create_reminder, schema=vol.Schema({
        vol.Required("text"): vol.All(str, vol.Length(min=1)),
        vol.Required("event_datetime"): str,
        vol.Optional("before"): list_or_str,
        vol.Optional("recipients"): list_or_str,
        vol.Optional("repeat", default="none"): vol.In(list(REPEATS)),
        vol.Optional("days"): list_or_str,
        vol.Optional("until"): str,
    }), supports_response=SupportsResponse.ONLY)

    hass.services.async_register(DOMAIN, "find_reminders", find_reminders, schema=vol.Schema({
        vol.Optional("search_text", default=""): str,
        vol.Optional("event_date", default=""): str,
    }), supports_response=SupportsResponse.ONLY)

    hass.services.async_register(DOMAIN, "delete_reminder", delete_reminder, schema=vol.Schema({
        vol.Required("search_text"): vol.All(str, vol.Length(min=3)),
        vol.Optional("event_date", default=""): str,
    }), supports_response=SupportsResponse.ONLY)

    hass.services.async_register(DOMAIN, "update_reminder", update_reminder, schema=vol.Schema({
        vol.Required("search_text"): vol.All(str, vol.Length(min=3)),
        vol.Optional("event_date", default=""): str,
        vol.Optional("new_text"): str,
        vol.Optional("new_event_datetime"): str,
        vol.Optional("new_before"): list_or_str,
        vol.Optional("new_recipients"): list_or_str,
        vol.Optional("new_repeat"): vol.Any("", vol.In(list(REPEATS))),
        vol.Optional("new_days"): list_or_str,
    }), supports_response=SupportsResponse.ONLY)

    return True
