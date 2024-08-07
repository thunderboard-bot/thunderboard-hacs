import logging
import asyncio
import aiohttp
import async_timeout
import voluptuous as vol

from datetime import timedelta
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers import config_validation as cv

from custom_components.thunderboard.diagnostics import ThunderboardDiagnostics

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

    # Register the play_sound service with schema
    service_schema = vol.Schema({
        vol.Required("sound_id"): cv.string,
    })
    hass.services.async_register(DOMAIN, "play_sound", coordinator.play_sound, schema=service_schema)

    # Add diagnostics entity
    async_add_entities = hass.data[DOMAIN][entry.entry_id].async_add_entities
    async_add_entities([ThunderboardDiagnostics(coordinator)])

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
                    sound_data = await response.json()

                async with self.session.get(f"{self.api_url}/status", headers=headers) as response:
                    if response.status != 200:
                        raise UpdateFailed(f"Error fetching status: {response.status}")
                    status_data = await response.json()

                return {**sound_data, **status_data}
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
