"""Lovelace card for Raccolta Differenziata integration."""

import os
import logging

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.lovelace.resources import ResourceStorageCollection

from ..const import DOMAIN


async def async_register_card(hass):
    """Register the Lovelace card."""
    # Ottieni il percorso del file JS della card
    # In Home Assistant, i file nella directory custom_components sono accessibili tramite /local/custom_components
    resource_url = f"/local/custom_components/{DOMAIN}/lovelace/raccolta-differenziata-card.js"
    
    # Verifica che il file esista
    card_dir = os.path.dirname(__file__)
    card_file = os.path.join(card_dir, "raccolta-differenziata-card.js")
    if not os.path.isfile(card_file):
        _LOGGER = logging.getLogger(__name__)
        _LOGGER.error(f"Card file not found: {card_file}")
        return
    
    # Aggiungi la risorsa JavaScript
    add_extra_js_url(hass, resource_url)
    
    # Registra la card nella collezione di risorse
    if "lovelace" in hass.data and "resources" in hass.data["lovelace"]:
        resources: ResourceStorageCollection = hass.data["lovelace"]["resources"]
        if resources and not any(r["url"] == resource_url for r in resources.async_items()):
            await resources.async_create_item(
                {
                    "url": resource_url,
                    "type": "module",
                    "res_type": "module",
                }
            )