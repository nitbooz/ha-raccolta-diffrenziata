"""Config flow for Raccolta Differenziata integration."""
import logging
import voluptuous as vol
from typing import Any, Dict, Optional

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_NAME

from .const import (
    DOMAIN,
    CONF_CONFERIMENTI,
    CONF_TIPO,
    CONF_GIORNO,
    CONF_FREQUENZA,
    CONF_COLORE,
    CONF_ICONA,
    CONF_NOTIFICHE,
    CONF_NOTIFICHE_ATTIVE,
    CONF_NOTIFICHE_ORARIO,
    CONF_NOTIFICHE_ANTICIPO,
    DEFAULT_ICON,
    DEFAULT_COLOR,
    DEFAULT_FREQUENCY,
    DEFAULT_NOTIFICATION_TIME,
    DEFAULT_NOTIFICATION_DAYS_BEFORE,
    FREQUENCY_WEEKLY,
    FREQUENCY_BIWEEKLY,
    FREQUENCY_MONTHLY,
    WEEKDAYS,
)

_LOGGER = logging.getLogger(__name__)

class RaccoltaDifferenziataConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Raccolta Differenziata."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._conferimenti = []
        self._notifiche = {
            CONF_NOTIFICHE_ATTIVE: True,
            CONF_NOTIFICHE_ORARIO: DEFAULT_NOTIFICATION_TIME,
            CONF_NOTIFICHE_ANTICIPO: DEFAULT_NOTIFICATION_DAYS_BEFORE,
        }

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Handle the initial step."""
        return await self.async_step_menu()

    async def async_step_menu(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Handle the menu step."""
        if user_input is not None:
            menu_option = user_input.get("menu")
            if menu_option == "conferimento":
                return await self.async_step_conferimento()
            elif menu_option == "notifiche":
                return await self.async_step_notifiche()
            elif menu_option == "complete":
                return self.async_create_entry(
                    title="Raccolta Differenziata",
                    data={
                        CONF_CONFERIMENTI: self._conferimenti,
                        CONF_NOTIFICHE: self._notifiche,
                    },
                )

        menu_options = ["conferimento", "notifiche"]
        if self._conferimenti:  # Solo se c'è almeno un conferimento configurato
            menu_options.append("complete")

        return self.async_show_form(
            step_id="menu",
            data_schema=vol.Schema(
                {
                    vol.Required("menu"): vol.In(
                        {
                            "conferimento": "Aggiungi conferimento",
                            "notifiche": "Configura notifiche",
                            "complete": "Completa configurazione",
                        }
                    ),
                }
            ),
        )

    async def async_step_conferimento(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Handle the conferimento step."""
        errors = {}

        if user_input is not None:
            # Valida i dati inseriti
            if user_input.get(CONF_GIORNO, "").lower() not in [day.lower() for day in WEEKDAYS]:
                errors[CONF_GIORNO] = "invalid_day"
            elif user_input.get(CONF_FREQUENZA, "").lower() not in [
                FREQUENCY_WEEKLY,
                FREQUENCY_BIWEEKLY,
                FREQUENCY_MONTHLY,
            ]:
                errors[CONF_FREQUENZA] = "invalid_frequency"
            else:
                # Aggiungi il conferimento alla lista
                self._conferimenti.append({
                    CONF_TIPO: user_input.get(CONF_TIPO, ""),
                    CONF_GIORNO: user_input.get(CONF_GIORNO, ""),
                    CONF_FREQUENZA: user_input.get(CONF_FREQUENZA, DEFAULT_FREQUENCY),
                    CONF_COLORE: user_input.get(CONF_COLORE, DEFAULT_COLOR),
                    CONF_ICONA: user_input.get(CONF_ICONA, DEFAULT_ICON),
                })
                return await self.async_step_add_another()

        # Mostra il form per configurare un conferimento
        return self.async_show_form(
            step_id="conferimento",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_TIPO): str,
                    vol.Required(CONF_GIORNO): vol.In(
                        {day: day.capitalize() for day in WEEKDAYS}
                    ),
                    vol.Required(CONF_FREQUENZA, default=DEFAULT_FREQUENCY): vol.In(
                        {
                            FREQUENCY_WEEKLY: "Settimanale",
                            FREQUENCY_BIWEEKLY: "Bisettimanale",
                            FREQUENCY_MONTHLY: "Mensile",
                        }
                    ),
                    vol.Optional(CONF_COLORE, default=DEFAULT_COLOR): str,
                    vol.Optional(CONF_ICONA, default=DEFAULT_ICON): str,
                }
            ),
            errors=errors,
        )

    async def async_step_add_another(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Ask if the user wants to add another conferimento."""
        if user_input is not None:
            if user_input.get("add_another", False):
                return await self.async_step_conferimento()
            return await self.async_step_menu()

        return self.async_show_form(
            step_id="add_another",
            data_schema=vol.Schema(
                {
                    vol.Required("add_another", default=True): bool,
                }
            ),
        )

    async def async_step_notifiche(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Handle the notifiche step."""
        errors = {}

        if user_input is not None:
            # Valida i dati inseriti
            try:
                orario = user_input.get(CONF_NOTIFICHE_ORARIO, DEFAULT_NOTIFICATION_TIME)
                hour, minute = map(int, orario.split(':'))
                if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                    errors[CONF_NOTIFICHE_ORARIO] = "invalid_time"
            except (ValueError, AttributeError):
                errors[CONF_NOTIFICHE_ORARIO] = "invalid_time"

            if not errors:
                # Aggiorna le impostazioni delle notifiche
                self._notifiche = {
                    CONF_NOTIFICHE_ATTIVE: user_input.get(CONF_NOTIFICHE_ATTIVE, True),
                    CONF_NOTIFICHE_ORARIO: user_input.get(CONF_NOTIFICHE_ORARIO, DEFAULT_NOTIFICATION_TIME),
                    CONF_NOTIFICHE_ANTICIPO: user_input.get(CONF_NOTIFICHE_ANTICIPO, DEFAULT_NOTIFICATION_DAYS_BEFORE),
                }
                return await self.async_step_menu()

        # Mostra il form per configurare le notifiche
        return self.async_show_form(
            step_id="notifiche",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NOTIFICHE_ATTIVE, default=self._notifiche.get(CONF_NOTIFICHE_ATTIVE, True)): bool,
                    vol.Required(CONF_NOTIFICHE_ORARIO, default=self._notifiche.get(CONF_NOTIFICHE_ORARIO, DEFAULT_NOTIFICATION_TIME)): str,
                    vol.Required(CONF_NOTIFICHE_ANTICIPO, default=self._notifiche.get(CONF_NOTIFICHE_ANTICIPO, DEFAULT_NOTIFICATION_DAYS_BEFORE)): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=7)
                    ),
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return RaccoltaDifferenziataOptionsFlow(config_entry)


class RaccoltaDifferenziataOptionsFlow(config_entries.OptionsFlow):
    """Handle options for the Raccolta Differenziata integration."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                # Qui puoi aggiungere opzioni configurabili dopo l'installazione
            }),
        )