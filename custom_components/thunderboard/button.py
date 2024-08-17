from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up Soundboard buttons from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Ensure coordinator.data is initialized
    if coordinator.data is None:
        coordinator.data = {"sounds": []}

    # Create initial button entities
    buttons = [SoundButton(coordinator, sound) for sound in coordinator.data["sounds"]]
    async_add_entities(buttons)

    # Register the method to add new entities
    coordinator.async_add_entities = async_add_entities

class SoundButton(CoordinatorEntity, ButtonEntity):
    def __init__(self, coordinator, sound):
        """Initialize the button."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self.sound = sound
        self._attr_name = sound["name"]
        self._attr_unique_id = f"button.thunderboard_{sound['id']}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.config_entry.entry_id)},
            "name": "Thunderboard Device",
            "manufacturer": "Thunderboard",
            "model": "Soundboard",
        }

    async def async_press(self) -> None:
        """Press the button."""
        await self.coordinator.play_sound(self.sound["id"])

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()