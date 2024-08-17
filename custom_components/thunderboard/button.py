from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up Soundboard sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Create initial sensor entities
    sensors = [SoundButton(coordinator, sound) for sound in coordinator.data["sounds"]]
    async_add_entities(sensors)

    # Register the method to add new entities
    coordinator.entities = sensors
    coordinator.async_add_entities = async_add_entities


class SoundButton(CoordinatorEntity, ButtonEntity):
    def __init__(self, coordinator, sound):
        """Initialize the button."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self.sound = sound
        self._attr_name = sound["name"]
        self._attr_unique_id = f"thunderboard_{sound['id']}"

    async def async_press(self) -> None:
        """Press the button."""
        await self.coordinator.play_sound(self.sound["id"])

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()
