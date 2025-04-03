"""Services for Raccolta Differenziata integration."""
import logging
from typing import Any, Dict, List

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import async_get_platforms

from .const import (
    DOMAIN,
    CONF_CONFERIMENTI,
    CONF_TIPO,
    CONF_GIORNO,
    CONF_FREQUENZA,
    CONF_COLORE,
    CONF_ICONA,
    DEFAULT_ICON,
    DEFAULT_COLOR,
    DEFAULT_FREQUENCY,
    WEEKDAYS,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for Raccolta Differenziata integration."""
    
    @callback
    async def update_collection(call: ServiceCall) -> None:
        """Update an existing waste collection."""
        tipo = call.data.get(CONF_TIPO)
        if not tipo:
            raise HomeAssistantError("Tipo di conferimento non specificato")
        
        # Trova l'entry di configurazione
        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            raise HomeAssistantError("Nessuna configurazione trovata per Raccolta Differenziata")
        
        entry = entries[0]  # Usa la prima entry trovata
        data = dict(entry.data)
        conferimenti = list(data.get(CONF_CONFERIMENTI, []))
        
        # Trova il conferimento da aggiornare
        for i, conferimento in enumerate(conferimenti):
            if conferimento.get(CONF_TIPO) == tipo:
                # Aggiorna i campi specificati
                for field in [CONF_GIORNO, CONF_FREQUENZA, CONF_COLORE, CONF_ICONA]:
                    if field in call.data:
                        conferimenti[i][field] = call.data[field]
                
                # Aggiorna la configurazione
                data[CONF_CONFERIMENTI] = conferimenti
                hass.config_entries.async_update_entry(entry, data=data)
                
                # Aggiorna i sensori
                for platform in async_get_platforms(hass, DOMAIN):
                    for entity in platform.entities.values():
                        if hasattr(entity, "async_schedule_update_ha_state"):
                            await entity.async_schedule_update_ha_state(True)
                
                return
        
        raise HomeAssistantError(f"Conferimento '{tipo}' non trovato")
    
    @callback
    async def add_collection(call: ServiceCall) -> None:
        """Add a new waste collection."""
        tipo = call.data.get(CONF_TIPO)
        giorno = call.data.get(CONF_GIORNO)
        frequenza = call.data.get(CONF_FREQUENZA)
        
        if not tipo or not giorno or not frequenza:
            raise HomeAssistantError("Dati mancanti per aggiungere un conferimento")
        
        # Valida il giorno
        if giorno.lower() not in [day.lower() for day in WEEKDAYS]:
            raise HomeAssistantError(f"Giorno non valido: {giorno}")
        
        # Trova l'entry di configurazione
        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            raise HomeAssistantError("Nessuna configurazione trovata per Raccolta Differenziata")
        
        entry = entries[0]  # Usa la prima entry trovata
        data = dict(entry.data)
        conferimenti = list(data.get(CONF_CONFERIMENTI, []))
        
        # Verifica se il tipo esiste già
        for conferimento in conferimenti:
            if conferimento.get(CONF_TIPO) == tipo:
                raise HomeAssistantError(f"Conferimento '{tipo}' già esistente")
        
        # Aggiungi il nuovo conferimento
        conferimenti.append({
            CONF_TIPO: tipo,
            CONF_GIORNO: giorno,
            CONF_FREQUENZA: frequenza,
            CONF_COLORE: call.data.get(CONF_COLORE, DEFAULT_COLOR),
            CONF_ICONA: call.data.get(CONF_ICONA, DEFAULT_ICON),
        })
        
        # Aggiorna la configurazione
        data[CONF_CONFERIMENTI] = conferimenti
        hass.config_entries.async_update_entry(entry, data=data)
        
        # Aggiorna i sensori
        for platform in async_get_platforms(hass, DOMAIN):
            for entity in platform.entities.values():
                if hasattr(entity, "async_schedule_update_ha_state"):
                    await entity.async_schedule_update_ha_state(True)
    
    @callback
    async def remove_collection(call: ServiceCall) -> None:
        """Remove an existing waste collection."""
        tipo = call.data.get(CONF_TIPO)
        if not tipo:
            raise HomeAssistantError("Tipo di conferimento non specificato")
        
        # Trova l'entry di configurazione
        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            raise HomeAssistantError("Nessuna configurazione trovata per Raccolta Differenziata")
        
        entry = entries[0]  # Usa la prima entry trovata
        data = dict(entry.data)
        conferimenti = list(data.get(CONF_CONFERIMENTI, []))
        
        # Trova e rimuovi il conferimento
        for i, conferimento in enumerate(conferimenti):
            if conferimento.get(CONF_TIPO) == tipo:
                del conferimenti[i]
                
                # Aggiorna la configurazione
                data[CONF_CONFERIMENTI] = conferimenti
                hass.config_entries.async_update_entry(entry, data=data)
                
                # Aggiorna i sensori
                for platform in async_get_platforms(hass, DOMAIN):
                    for entity in platform.entities.values():
                        if hasattr(entity, "async_schedule_update_ha_state"):
                            await entity.async_schedule_update_ha_state(True)
                
                return
        
        raise HomeAssistantError(f"Conferimento '{tipo}' non trovato")
    
    # Registra i servizi
    hass.services.async_register(DOMAIN, "update_collection", update_collection)
    hass.services.async_register(DOMAIN, "add_collection", add_collection)
    hass.services.async_register(DOMAIN, "remove_collection", remove_collection)

async def async_unload_services(hass: HomeAssistant) -> None:
    """Unload Raccolta Differenziata services."""
    # Rimuovi i servizi registrati
    hass.services.async_remove(DOMAIN, "update_collection")
    hass.services.async_remove(DOMAIN, "add_collection")
    hass.services.async_remove(DOMAIN, "remove_collection")