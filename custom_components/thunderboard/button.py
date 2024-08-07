from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up Soundboard sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Create sensor entities
    sensors = [SoundButton(coordinator, sound) for sound in coordinator.data["sounds"]]
    async_add_entities(sensors)


class SoundButton(ButtonEntity):
    def __init__(self, coordinator, sound):
        """Initialize the button."""
        self.coordinator = coordinator
        self.sound = sound
        self._attr_name = sound["name"]
        self._attr_unique_id = sound["id"]

    async def async_press(self) -> None:
        """Press the button."""
        await self.coordinator.play_sound(self.sound["id"])
