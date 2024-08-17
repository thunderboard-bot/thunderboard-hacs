import logging
import async_timeout

from datetime import timedelta
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from custom_components.thunderboard.button import SoundButton
from custom_components.thunderboard.diagnostics import ThunderboardConnectionState, ThunderboardCurrentChannel

DOMAIN = "thunderboard"
PLATFORMS = ["sensor", "button"]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Soundboard from a config entry."""
    coordinator = SoundboardDataUpdateCoordinator(hass, entry.data)
    await coordinator.async_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    for component in PLATFORMS:
        hass.async_add_job(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    async def handle_reconfigure(call):
        """Handle the service call to reconfigure the integration."""
        await coordinator.reconfigure()

    hass.services.async_register(DOMAIN, "reconfigure", handle_reconfigure)

    return True


class SoundboardDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, config):
        """Initialize the coordinator."""
        self.hass = hass
        self.config = config
        self.session = async_get_clientsession(hass)
        self.api_url = config["service_url"]
        self.token = config["access_token"]
        self.sounds = []
        self.entities = []
        self.data = {"sounds": [], "status": {}}

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )

    async def _async_update_data(self):
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

                async with self.session.get(f"{self.api_url}/status", headers=headers) as response:
                    if response.status == 404:
                        raise UpdateFailed("Error fetching status: 404 Not Found")
                    if response.status != 200:
                        raise UpdateFailed(f"Error fetching status: {response.status}")
                    status_data = await response.json()

                # Ensure sound_data is a list and status_data is a dictionary
                if not isinstance(sound_data, list) or not isinstance(status_data, dict):
                    raise UpdateFailed("Unexpected data format")

                # Update sounds and notify entities if there are new sounds
                if sound_data != self.sounds:
                    new_sounds = [sound for sound in sound_data if sound not in self.sounds]
                    self.sounds = sound_data
                    self.async_update_listeners()
                    self._add_new_entities(new_sounds)

                self.data = {"sounds": sound_data, **status_data}
                return self.data
        except Exception as e:
            raise UpdateFailed(f"Error fetching data: {e}")

    def _add_new_entities(self, new_sounds):
        """Add new sound entities."""
        if new_sounds:
            new_entities = [SoundButton(self, sound) for sound in new_sounds]
            self.entities.extend(new_entities)
            self.hass.add_job(self.hass.config_entries.async_forward_entry_setup(self.config, "button"))

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
        self.hass.config_entries.async_forward_entry_setup(self.config, "button")
