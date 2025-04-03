"""Sensor platform for Raccolta Differenziata integration."""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ICON, CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed, CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    CONF_CONFERIMENTI,
    CONF_TIPO,
    CONF_GIORNO,
    CONF_FREQUENZA,
    CONF_COLORE,
    CONF_ICONA,
    TRANSLATIONS,
    WEEKDAYS,
    WEEKDAYS_EN,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up the Raccolta Differenziata sensor platform."""
    conferimenti = entry.data.get(CONF_CONFERIMENTI, [])
    
    if not conferimenti:
        return
    
    # Crea un coordinatore per aggiornare i dati
    coordinator = RaccoltaDifferenziataCoordinator(hass, conferimenti)
    await coordinator.async_config_entry_first_refresh()
    
    # Crea i sensori
    sensors = [
        RaccoltaDifferenziataSensor(coordinator, 0, "next"),  # Prossimo conferimento
        RaccoltaDifferenziataSensor(coordinator, 1, "next_plus_one"),  # Secondo conferimento
        RaccoltaDifferenziataSensor(coordinator, 2, "next_plus_two"),  # Terzo conferimento
    ]
    
    async_add_entities(sensors, True)


class RaccoltaDifferenziataCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Raccolta Differenziata data."""

    def __init__(self, hass: HomeAssistant, conferimenti: List[Dict[str, Any]]) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=1),  # Aggiorna ogni ora
        )
        self.conferimenti = conferimenti
        self.upcoming_collections = []

    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from API endpoint."""
        try:
            # Calcola i prossimi conferimenti
            today = datetime.now().date()
            upcoming = []
            
            for conferimento in self.conferimenti:
                next_date = self._get_next_date(conferimento, today)
                upcoming.append({
                    "date": next_date,
                    "tipo": conferimento.get(CONF_TIPO),
                    "icon": conferimento.get(CONF_ICONA, "mdi:recycle"),
                    "color": conferimento.get(CONF_COLORE, "#4CAF50"),
                    "frequency": conferimento.get(CONF_FREQUENZA),
                })
            
            # Ordina per data
            upcoming.sort(key=lambda x: x["date"])
            self.upcoming_collections = upcoming
            
            return {"collections": upcoming}
        except Exception as err:
            raise UpdateFailed(f"Error updating Raccolta Differenziata data: {err}") from err

    def _get_next_date(self, conferimento: Dict[str, Any], today: datetime.date) -> datetime.date:
        """Calculate the next date for a specific waste collection."""
        giorno = conferimento.get(CONF_GIORNO).lower()
        frequenza = conferimento.get(CONF_FREQUENZA, "settimanale").lower()
        
        # Converti il giorno in indice numerico (0 = lunedì, 6 = domenica)
        if giorno in WEEKDAYS:
            day_index = WEEKDAYS.index(giorno)
        elif giorno in WEEKDAYS_EN:
            day_index = WEEKDAYS_EN.index(giorno)
        else:
            # Default a lunedì se il giorno non è valido
            day_index = 0
        
        # Calcola il prossimo giorno della settimana
        days_ahead = day_index - today.weekday()
        if days_ahead <= 0:  # Se è oggi o è già passato questa settimana
            days_ahead += 7
        
        next_date = today + timedelta(days=days_ahead)
        
        # Gestisci frequenze diverse da settimanale
        if frequenza == "bisettimanale":
            # Verifica se la prossima data è nella settimana corretta
            # Assumiamo che la raccolta bisettimanale inizi dalla prima settimana dell'anno
            week_number = next_date.isocalendar()[1]
            if week_number % 2 != 1:  # Se non è una settimana dispari
                next_date += timedelta(days=7)  # Aggiungi un'altra settimana
        elif frequenza == "mensile":
            # Assumiamo che la raccolta mensile sia il primo giorno specificato del mese
            if next_date.day > 7:  # Se siamo oltre la prima settimana del mese
                # Vai al prossimo mese
                if next_date.month == 12:
                    next_month = 1
                    next_year = next_date.year + 1
                else:
                    next_month = next_date.month + 1
                    next_year = next_date.year
                
                # Trova il primo giorno della settimana specificato nel prossimo mese
                first_day = datetime(next_year, next_month, 1).date()
                days_ahead = (day_index - first_day.weekday()) % 7
                next_date = first_day + timedelta(days=days_ahead)
        
        return next_date


class RaccoltaDifferenziataSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Raccolta Differenziata sensor."""

    def __init__(self, coordinator: RaccoltaDifferenziataCoordinator, index: int, sensor_type: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.index = index
        self.sensor_type = sensor_type
        self._attr_unique_id = f"{DOMAIN}_{sensor_type}"
        self._attr_name = f"Raccolta Differenziata {sensor_type.replace('_', ' ').title()}"
        self._attr_icon = "mdi:recycle"
        
    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success and len(self.coordinator.upcoming_collections) > self.index

    @property
    def state(self) -> Optional[str]:
        """Return the state of the sensor."""
        if not self.available:
            return None
        
        collection = self.coordinator.upcoming_collections[self.index]
        return collection["tipo"]

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = {}
        
        if self.available:
            collection = self.coordinator.upcoming_collections[self.index]
            date = collection["date"]
            
            # Ottieni il nome del giorno della settimana in italiano
            weekday_index = date.weekday()
            weekday_name = WEEKDAYS[weekday_index]
            
            attrs["date"] = date.isoformat()
            attrs["weekday"] = weekday_name
            attrs["icon"] = collection["icon"]
            attrs["color"] = collection["color"]
            attrs["frequency"] = collection["frequency"]
            attrs["days_until"] = (date - datetime.now().date()).days
        
        return attrs