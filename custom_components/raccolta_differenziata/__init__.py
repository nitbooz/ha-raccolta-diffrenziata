"""The Raccolta Differenziata integration."""
import asyncio
import logging
from datetime import datetime, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_change
from homeassistant.util import dt as dt_util

from .lovelace import async_register_card
from .services import async_setup_services, async_unload_services

from .const import (
    DOMAIN,
    CONF_CONFERIMENTI,
    CONF_NOTIFICHE,
    CONF_NOTIFICHE_ATTIVE,
    CONF_NOTIFICHE_ORARIO,
    CONF_NOTIFICHE_ANTICIPO,
    DEFAULT_NOTIFICATION_TIME,
    DEFAULT_NOTIFICATION_DAYS_BEFORE,
    TRANSLATIONS,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Raccolta Differenziata from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Registra i sensori
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Configura le notifiche se abilitate
    notifiche = entry.data.get(CONF_NOTIFICHE, {})
    if notifiche.get(CONF_NOTIFICHE_ATTIVE, False):
        await _setup_notifications(hass, entry)
    
    # Registra i servizi
    await async_setup_services(hass)
    
    # Registra la card Lovelace
    await async_register_card(hass)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    # Rimuovi i dati dell'integrazione
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

async def _setup_notifications(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Set up notifications for waste collection reminders."""
    notifiche = entry.data.get(CONF_NOTIFICHE, {})
    orario = notifiche.get(CONF_NOTIFICHE_ORARIO, DEFAULT_NOTIFICATION_TIME)
    anticipo = notifiche.get(CONF_NOTIFICHE_ANTICIPO, DEFAULT_NOTIFICATION_DAYS_BEFORE)
    
    # Estrai ora e minuti dall'orario configurato
    try:
        hour, minute = map(int, orario.split(':'))
    except (ValueError, AttributeError):
        _LOGGER.error("Invalid notification time format: %s. Using default 19:00", orario)
        hour, minute = 19, 0

    # Registra un listener per l'orario specificato
    async def check_notifications(now):
        """Check if there are waste collections to notify about."""
        # Ottieni la lingua configurata in Home Assistant
        language = hass.config.language or "en"
        translations = TRANSLATIONS.get(language, TRANSLATIONS["en"])
        
        # Ottieni i conferimenti configurati
        conferimenti = entry.data.get(CONF_CONFERIMENTI, [])
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        
        # Controlla se ci sono conferimenti per domani o oggi (in base all'anticipo configurato)
        for conferimento in conferimenti:
            tipo = conferimento.get("tipo", "")
            giorno = conferimento.get("giorno", "").lower()
            frequenza = conferimento.get("frequenza", "settimanale").lower()
            
            # Calcola la prossima data di conferimento
            from .sensor import RaccoltaDifferenziataCoordinator
            coordinator = RaccoltaDifferenziataCoordinator(hass, [conferimento])
            next_date = coordinator._get_next_date(conferimento, today)
            
            # Verifica se la data è entro il periodo di notifica
            days_until = (next_date - today).days
            if days_until <= anticipo:
                # Invia notifica
                if days_until == 0:
                    message = translations["notification_message_today"].format(tipo)
                else:
                    message = translations["notification_message"].format(tipo)
                
                await hass.services.async_call(
                    "notify",
                    "mobile_app",  # Usa il servizio mobile_app per le notifiche push
                    {
                        "title": translations["notification_title"],
                        "message": message,
                        "data": {
                            "tag": f"raccolta_differenziata_{tipo}",
                            "color": conferimento.get("colore", "#4CAF50"),
                            "icon": conferimento.get("icona", "mdi:recycle"),
                        },
                    },
                )

    # Registra il listener per l'orario specificato
    async_track_time_change(hass, check_notifications, hour=hour, minute=minute, second=0)