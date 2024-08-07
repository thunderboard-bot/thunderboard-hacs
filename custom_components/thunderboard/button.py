from homeassistant.components.button import ButtonEntity


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
