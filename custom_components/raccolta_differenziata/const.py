"""Constants for the Raccolta Differenziata integration."""

DOMAIN = "raccolta_differenziata"

# Configuration constants
CONF_CONFERIMENTI = "conferimenti"
CONF_TIPO = "tipo"
CONF_GIORNO = "giorno"
CONF_FREQUENZA = "frequenza"
CONF_COLORE = "colore"
CONF_ICONA = "icona"
CONF_NOTIFICHE = "notifiche"
CONF_NOTIFICHE_ATTIVE = "attive"
CONF_NOTIFICHE_ORARIO = "orario"
CONF_NOTIFICHE_ANTICIPO = "anticipo"

# Default values
DEFAULT_ICON = "mdi:recycle"
DEFAULT_COLOR = "#4CAF50"
DEFAULT_FREQUENCY = "settimanale"
DEFAULT_NOTIFICATION_TIME = "19:00"
DEFAULT_NOTIFICATION_DAYS_BEFORE = 1

# Frequency options
FREQUENCY_WEEKLY = "settimanale"
FREQUENCY_BIWEEKLY = "bisettimanale"
FREQUENCY_MONTHLY = "mensile"

# Days of the week (Italian)
WEEKDAYS = [
    "lunedì",
    "martedì",
    "mercoledì",
    "giovedì",
    "venerdì",
    "sabato",
    "domenica",
]

# Days of the week (English)
WEEKDAYS_EN = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]

# Translations for UI
TRANSLATIONS = {
    "it": {
        "next_collection": "Prossimo conferimento",
        "days_until": "tra {} giorni",
        "tomorrow": "domani",
        "today": "oggi",
        "notification_title": "Promemoria raccolta differenziata",
        "notification_message": "Domani è previsto il conferimento di {}",
        "notification_message_today": "Oggi è previsto il conferimento di {}",
    },
    "en": {
        "next_collection": "Next waste collection",
        "days_until": "in {} days",
        "tomorrow": "tomorrow",
        "today": "today",
        "notification_title": "Waste collection reminder",
        "notification_message": "Tomorrow is scheduled for {} collection",
        "notification_message_today": "Today is scheduled for {} collection",
    },
}