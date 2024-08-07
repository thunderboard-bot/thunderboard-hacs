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

from custom_components.thunderboard.diagnostics import ThunderboardConnectionState, ThunderboardCurrentChannel

DOMAIN = "thunderboard"
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

                # Ensure sound_data is a list and status_data is a dictionary
                if not isinstance(sound_data, list) or not isinstance(status_data, dict):
                    raise UpdateFailed("Unexpected data format")

                return {"sounds": sound_data, **status_data}
        except Exception as e:
            raise UpdateFailed(f"Error fetching data: {e}")

    async def play_sound(self, call):
        """Play a sound."""
        sound_id = call.data["sound_id"]
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
