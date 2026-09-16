"""Utility Cost integration."""
from __future__ import annotations

from datetime import timedelta
import logging
from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval

from .const import DOMAIN, PLATFORMS
from .engine import CostEngine

_LOGGER = logging.getLogger(__name__)
CARD_VERSION = "1.1.0"
CARD_PATH = Path(__file__).parent / "frontend" / "utility-cost-card.js"
BILL_CARD_PATH = Path(__file__).parent / "frontend" / "utility-bill-card.js"
CARD_URL = "/utility_cost_static/utility-cost-card.js"
BILL_CARD_URL = "/utility_cost_static/utility-bill-card.js"
CARD_MODULE_URL = f"{CARD_URL}?v={CARD_VERSION.replace('.', '')}"
BILL_CARD_MODULE_URL = f"{BILL_CARD_URL}?v={CARD_VERSION.replace('.', '')}"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up Utility Cost and expose the bundled Lovelace card."""
    await hass.http.async_register_static_paths(
        [StaticPathConfig(CARD_URL, str(CARD_PATH), False), StaticPathConfig(BILL_CARD_URL, str(BILL_CARD_PATH), False)]
    )
    # Load the bundled card globally. This is intentionally independent of
    # Lovelace storage resources, so it also works with YAML dashboards.
    add_extra_js_url(hass, CARD_MODULE_URL)
    add_extra_js_url(hass, BILL_CARD_MODULE_URL)
    _LOGGER.info("Utility Cost card registered at %s", CARD_MODULE_URL)
    return True


async def async_setup_entry(hass: HomeAssistant, entry) -> bool:
    """Set up a Utility Cost config entry."""
    eng = CostEngine(hass, entry)
    await eng.load()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = eng

    async def _tick(now):
        await eng.tick(now)

    entry.async_on_unload(
        async_track_time_interval(hass, _tick, timedelta(minutes=1))
    )
    entry.async_on_unload(entry.add_update_listener(_reload))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def _reload(hass: HomeAssistant, entry) -> None:
    """Reload after options/config changes."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry) -> bool:
    """Unload a Utility Cost config entry."""
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return ok
