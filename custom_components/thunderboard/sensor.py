import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Soundboard sensors."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(SoundboardSensor(coordinator, sound) for sound in coordinator.data)

class SoundboardSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, sound):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.sound = sound
        self._attr_unique_id = f"soundboard_{sound['id']}"
        self._attr_name = sound["name"]

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.sound["id"]

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "submitted_by": self.sound.get("submittedBy"),
            "tags": self.sound.get("tags", []),
            "favorite": self.sound.get("favorite", False),
        }

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.sound = self.coordinator.data.get(self.sound["id"], self.sound)
        self.async_write_ha_state()
