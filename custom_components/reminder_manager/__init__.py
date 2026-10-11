"""Reminder Manager for Home Assistant."""

from datetime import datetime, timedelta
import logging
import re
import unicodedata

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.exceptions import HomeAssistantError
from homeassistant.components.calendar import CalendarEntityFeature
from homeassistant.util import dt as dt_util

DOMAIN = "reminder_manager"
CALENDAR = "calendar.reminders"

_LOGGER = logging.getLogger(__name__)

EVENT_DATE_PATTERN = re.compile(
    r"Ραντεβού/γεγονός:\s*(\d{2}/\d{2}/\d{4})"
)


def normalize(value: str) -> str:
    """Normalize Greek text for searching."""
    value = unicodedata.normalize("NFD", value.casefold())
    return "".join(
        char for char in value
        if unicodedata.category(char) != "Mn"
    )


def get_event_date(event) -> str:
    """Get the appointment date, rather than the notification date."""
    description = event.description or ""
    match = EVENT_DATE_PATTERN.search(description)

    if match:
        try:
            return datetime.strptime(
                match.group(1), "%d/%m/%Y"
            ).date().isoformat()
        except ValueError:
            pass

    # For events without our reminder metadata,
    # fall back to the calendar event's start date.
    return event.start.date().isoformat() if isinstance(
        event.start, datetime
    ) else event.start.isoformat()


def event_info(event) -> dict:
    """Return safe information for the conversation agent."""
    return {
        "summary": event.summary,
        "event_date": get_event_date(event),
        "notification_start": event.start.isoformat(),
        "description": event.description or "",
    }


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Register reminder services."""

    async def delete_reminder(call: ServiceCall) -> dict:
        search_text = call.data["search_text"].strip()
        event_date = call.data.get("event_date", "").strip()

        if len(search_text) < 3:
            return {
                "status": "invalid",
                "message": "Χρειάζονται τουλάχιστον τρεις χαρακτήρες αναζήτησης."
            }

        if event_date:
            try:
                event_date = datetime.strptime(
                    event_date, "%Y-%m-%d"
                ).date().isoformat()
            except ValueError:
                return {
                    "status": "invalid",
                    "message": "Η ημερομηνία πρέπει να είναι YYYY-MM-DD."
                }

        calendar_component = hass.data.get("calendar")

        if calendar_component is None:
            return {
                "status": "error",
                "message": "Το calendar integration δεν είναι διαθέσιμο."
            }

        entity = calendar_component.get_entity(CALENDAR)

        if entity is None:
            return {
                "status": "error",
                "message": "Δεν βρέθηκε το calendar.reminders."
            }

        if not (
            entity.supported_features
            and entity.supported_features
            & CalendarEntityFeature.DELETE_EVENT
        ):
            return {
                "status": "error",
                "message": "Το ημερολόγιο δεν υποστηρίζει διαγραφή."
            }

        start = dt_util.now()
        end = start + timedelta(days=730)

        try:
            events = await entity.async_get_events(
                hass, start, end
            )

            query = normalize(search_text)

            matches = [
                event
                for event in events
                if (
                    query in normalize(event.summary or "")
                    or query in normalize(event.description or "")
                )
                and (
                    not event_date
                    or get_event_date(event) == event_date
                )
            ]

            if not matches:
                return {
                    "status": "not_found",
                    "message": "Δεν βρέθηκε υπενθύμιση με αυτά τα στοιχεία.",
                    "search_text": search_text,
                    "event_date": event_date
                }

            if len(matches) > 1:
                return {
                    "status": "multiple_matches",
                    "message": "Βρέθηκαν περισσότερες από μία υπενθυμίσεις. Χρειάζεται διευκρίνιση.",
                    "events": [
                        event_info(event)
                        for event in matches[:20]
                    ]
                }

            event = matches[0]

            if not event.uid:
                return {
                    "status": "error",
                    "message": "Η υπενθύμιση δεν έχει αναγνωριστικό διαγραφής."
                }

            # Do not risk deleting an entire recurring series.
            if event.rrule or event.recurrence_id:
                return {
                    "status": "error",
                    "message": "Η αυτόματη διαγραφή επαναλαμβανόμενων υπενθυμίσεων δεν υποστηρίζεται ακόμη."
                }

            await entity.async_delete_event(event.uid)

            return {
                "status": "deleted",
                **event_info(event),
                "message": "Η υπενθύμιση διαγράφηκε επιτυχώς."
            }

        except (HomeAssistantError, ValueError) as err:
            _LOGGER.exception("Reminder deletion failed")
            return {
                "status": "error",
                "message": str(err)
            }

    hass.services.async_register(
        DOMAIN,
        "delete_reminder",
        delete_reminder,
        schema=vol.Schema({
            vol.Required("search_text"): vol.All(
                str, vol.Length(min=3)
            ),
            vol.Optional("event_date", default=""): str,
        }),
        supports_response=SupportsResponse.ONLY
    )

    return True