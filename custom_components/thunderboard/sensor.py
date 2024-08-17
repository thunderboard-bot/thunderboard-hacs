import logging
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant

from . import DOMAIN
from .diagnostics import ThunderboardConnectionState, ThunderboardCurrentChannel

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up Soundboard sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Add diagnostics entities
    async_add_entities([
        ThunderboardConnectionState(coordinator,
                                    SensorEntityDescription(
                                        entity_category=EntityCategory.DIAGNOSTIC
                                    )),
        ThunderboardCurrentChannel(coordinator,
                                   SensorEntityDescription(
                                       entity_category=EntityCategory.DIAGNOSTIC
                                   ))]
    )
