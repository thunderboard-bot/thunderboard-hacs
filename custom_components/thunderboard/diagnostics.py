from homeassistant.components.sensor import SensorEntity
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


class ThunderboardDiagnostics(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        """Initialize the diagnostics sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"thunderboard_diagnostics"
        self._attr_name = "Thunderboard Diagnostics"

    @property
    def state(self):
        """Return the state of the diagnostics sensor."""
        return "connected" if self.coordinator.data["connected"] else "disconnected"

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "current_channel": self.coordinator.data.get("currentChannel"),
        }

    @property
    def device_info(self):
        """Return device information about this entity."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.config_entry.entry_id)},
            "name": "Thunderboard",
            "manufacturer": "Your Company",
            "model": "Thunderboard Model",
            "sw_version": "1.0.1",
        }

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()