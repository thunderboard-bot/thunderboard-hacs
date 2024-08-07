import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback, HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DOMAIN, ThunderboardDiagnostics

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up Soundboard sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Create sensor entities
    sensors = [SoundboardSensor(coordinator, sound) for sound in coordinator.data["sounds"]]
    async_add_entities(sensors)

    # Add diagnostics entity
    async_add_entities([ThunderboardDiagnostics(coordinator)])

class SoundboardSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, sound):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.sound = sound
        self._attr_unique_id = f"thunderboard_{sound['id']}"
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

    @property
    def device_info(self):
        """Return device information about this entity."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.config_entry.entry_id)},
            "name": "Thunderboard",
            "manufacturer": "Thunderboard Bot",
            "model": "Thunderboard API",
            "sw_version": "1.0.2",
        }

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
