"""Config flow for Thunderboard integration."""
from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_ACCESS_TOKEN, CONF_URL
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, LOGGER

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ACCESS_TOKEN): str,
        vol.Required(CONF_URL): str,
    }
)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Thunderboard."""

    VERSION = 1

    async def _validate_input(self, data: dict[str, Any]) -> dict[str, str]:
        """Validate the user input allows us to connect."""
        errors: dict[str, str] = {}
        access_token: str = data[CONF_ACCESS_TOKEN]
        service_url: str = data[CONF_URL]

        session = async_get_clientsession(self.hass)
        headers = {"Auth-Token": access_token}

        try:
            async with session.get(f"{service_url}/api/sound", headers=headers) as response:
                if response.status != 200:
                    errors["base"] = "cannot_connect"
        except Exception as exception:  # pylint: disable=broad-except
            LOGGER.exception(exception)
            errors["base"] = "unknown"

        return errors

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA)

        errors = await self._validate_input(user_input)
        if not errors:
            unique_id = user_input[CONF_URL]
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title="Thunderboard", data=user_input)

        return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors)