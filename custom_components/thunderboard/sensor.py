import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback, HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DOMAIN, ThunderboardConnectionState, ThunderboardCurrentChannel

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up Soundboard sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Add diagnostics entities
    async_add_entities([ThunderboardConnectionState(coordinator), ThunderboardCurrentChannel(coordinator)])
