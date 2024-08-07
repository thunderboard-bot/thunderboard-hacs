import logging
import asyncio
import aiohttp
import async_timeout

from datetime import timedelta
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

DOMAIN = "soundboard"
PLATFORMS = ["sensor"]

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

    hass.services.async_register(DOMAIN, "play_sound", coordinator.play_sound)

    return True

class SoundboardDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, config):
        """Initialize the coordinator."""
        self.hass = hass
        self.config = config
        self.session = async_get_clientsession(hass)
        self.api_url = config["service_url"]
        self.token = config["access_token"]

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=10),
        )

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            async with async_timeout.timeout(10):
                headers = {"Auth-Token": self.token}
                async with self.session.get(f"{self.api_url}/api/sound", headers=headers) as response:
                    if response.status != 200:
                        raise UpdateFailed(f"Error fetching data: {response.status}")
                    return await response.json()
        except Exception as e:
            raise UpdateFailed(f"Error fetching data: {e}")

    async def play_sound(self, call):
        """Play a sound."""
        sound_id = call.data["sound_id"]
        headers = {"Auth-Token": self.token}
        async with self.session.post(f"{self.api_url}/api/sound/{sound_id}/play", headers=headers) as response:
            if response.status != 200:
                _LOGGER.error(f"Error playing sound: {response.status}")
            else:
                _LOGGER.info(f"Played sound: {sound_id}")
