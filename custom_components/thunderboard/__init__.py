"""Thunderboard Soundboard bot integration."""
import logging
import async_timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_URL, CONF_ACCESS_TOKEN
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .button import SoundButton
from .const import DOMAIN, PLATFORMS, LOGGER, COORDINATOR_UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Soundboard from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    dev_reg = dr.async_get(hass)

    hass.data[DOMAIN][entry.entry_id] = coordinator = SoundboardDataUpdateCoordinator(hass, entry, dev_reg=dev_reg)

    await coordinator.async_config_entry_first_refresh()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

class SoundboardDataUpdateCoordinator(DataUpdateCoordinator):
    """Data update coordinator for Soundboard."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, dev_reg: dr.DeviceRegistry) -> None:
        """Initialize the coordinator."""
        self.hass = hass
        self.config_entry = entry
        self.session = async_get_clientsession(hass)
        self.api_url = entry.data[CONF_URL]
        self.token = entry.data[CONF_ACCESS_TOKEN]
        self.sounds = []
        self.entities = []
        self.data = {"sounds": [], "status": {}}
        self._device_registry = dev_reg

        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=COORDINATOR_UPDATE_INTERVAL,
        )

    async def _async_update_data(self) -> dict | None:
        """Fetch data from API."""
        try:
            async with async_timeout.timeout(10):
                headers = {"Auth-Token": self.token}
                async with self.session.get(f"{self.api_url}/api/sound", headers=headers) as response:
                    if response.status == 404:
                        raise UpdateFailed("Error fetching data: 404 Not Found")
                    if response.status != 200:
                        raise UpdateFailed(f"Error fetching data: {response.status}")
                    sound_data = await response.json()

                async with self.session.get(f"{self.api_url}/api/status", headers=headers) as response:
                    if response.status == 404:
                        raise UpdateFailed("Error fetching status: 404 Not Found")
                    if response.status != 200:
                        raise UpdateFailed(f"Error fetching status: {response.status}")
                    status_data = await response.json()

                # Ensure sound_data is a list and status_data is a dictionary
                if not isinstance(sound_data, list) or not isinstance(status_data, dict):
                    raise UpdateFailed("Unexpected data format")

                current_sounds = {
                    str(entity.unique_id)
                    for entity in self._device_registry.async_entries_for_config_entry(
                        self.config_entry.entry_id
                    )
                }
                new_sounds = {str(sound["id"]) for sound in sound_data}
                _LOGGER.debug(f"Current sounds: {current_sounds}")
                _LOGGER.debug(f"New sounds: {new_sounds}")

                if stale_sounds := current_sounds - new_sounds:
                    _LOGGER.debug(f"Stale sounds: {stale_sounds}")
                    for sound_id in stale_sounds:
                        if device := self._device_registry.async_get_device(
                                {(DOMAIN, sound_id)}
                        ):
                            self._device_registry.async_remove_device(device.id)

                # If there are new sounds, reload the config entry so we can
                # create new devices and entities.
                if self.data and new_sounds - {
                    str(sound["id"]) for sound in self.data["sounds"]
                }:
                    self.hass.async_create_task(
                        self.hass.config_entries.async_reload(self.config_entry.entry_id)
                    )
                    return None

                self.data = {"sounds": sound_data, **status_data}
                return self.data
        except Exception as e:
            raise UpdateFailed(f"Error fetching data: {e}")

    async def play_sound(self, sound_id):
        """Play a sound."""
        headers = {
            "Auth-Token": self.token,
            "Content-Type": "application/json"
        }
        request_path = f"{self.api_url}/api/sound/{sound_id}/play"

        async with self.session.post(request_path, headers=headers) as response:
            if response.status != 200:
                error_message = await response.text()
                _LOGGER.error(f"Failed to play sound: {error_message}")
                raise Exception(f"Error playing sound: {response.status}")
            else:
                _LOGGER.info(f"Playing sound {sound_id}")

    async def reconfigure(self):
        """Reconfigure the integration by clearing and re-adding entities."""
        # Clear existing entities
        for entity in self.entities:
            await entity.async_remove()
        self.entities.clear()

        # Refresh data and re-add entities
        await self.async_refresh()
        new_entities = [SoundButton(self, sound) for sound in self.sounds]
        self.entities.extend(new_entities)
        self.hass.config_entries.async_forward_entry_setup(self.config_entry, "button")