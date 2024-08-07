import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from .const import DOMAIN


@config_entries.HANDLERS.register(DOMAIN)
class SoundboardConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Soundboard."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize the config flow."""
        self._errors = {}

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return await self._validate_and_create_entry(user_input)

        return self._show_config_form(user_input or {})

    @callback
    def _show_config_form(self, user_input):
        """Show the configuration form to edit location data."""
        data_schema = vol.Schema(
            {
                vol.Required("access_token", default=user_input.get("access_token", ""),
                             description="Access Token"): str,
                vol.Required("service_url", default=user_input.get("service_url", ""), description="Service URL"): str,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=self._errors
        )

    async def _validate_and_create_entry(self, user_input):
        """Validate the user input and create the config entry."""
        self._errors = {}

        # Validate the provided data
        try:
            valid = await self._validate_input(user_input)
            if not valid:
                self._errors["base"] = "auth"
        except Exception:  # pylint: disable=broad-except
            self._errors["base"] = "auth"

        if self._errors:
            return self._show_config_form(user_input)

        return self.async_create_entry(
            title="Thunderboard", data=user_input
        )

    async def _validate_input(self, data):
        """Validate the input data."""
        # Here you can add actual validation of the access_token and service_url
        # For now, we will assume the provided input is valid
        return True

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return SoundboardOptionsFlowHandler(config_entry)


class SoundboardOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Soundboard options."""

    def __init__(self, config_entry):
        """Initialize Soundboard options flow."""
        self.config_entry = config_entry
        self._errors = {}

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return await self._validate_and_update_options(user_input)

        return self._show_options_form(user_input)

    @callback
    def _show_options_form(self, user_input):
        """Show the options form to edit options."""
        options_schema = vol.Schema(
            {
                vol.Required("access_token", default=self.config_entry.options.get("access_token", ""), description="Access Token"): str,
                vol.Required("service_url", default=self.config_entry.options.get("service_url", ""), description="Service URL"): str,
            }
        )

        return self.async_show_form(
            step_id="init", data_schema=options_schema, errors=self._errors
        )

    async def _validate_and_update_options(self, user_input):
        """Validate and update the options."""
        self._errors = {}

        # Validate the provided data
        try:
            valid = await self._validate_input(user_input)
            if not valid:
                self._errors["base"] = "auth"
        except Exception:  # pylint: disable=broad-except
            self._errors["base"] = "auth"

        if self._errors:
            return self._show_options_form(user_input)

        self.hass.config_entries.async_update_entry(
            self.config_entry, options=user_input
        )
        return self.async_create_entry(
            title="", data={}
        )

    async def _validate_input(self, data):
        """Validate the input data."""
        # Here you can add actual validation of the access_token and service_url
        # For now, we will assume the provided input is valid
        return True
