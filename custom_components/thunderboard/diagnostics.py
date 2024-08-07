from homeassistant.components.sensor import SensorEntity
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


class ThunderboardConnectionState(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        """Initialize the connection state sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"thunderboard_connection_state"
        self._attr_name = "Thunderboard Connection State"

    @property
    def state(self):
        """Return the state of the connection."""
        return "connected" if self.coordinator.data["connected"] else "disconnected"

    @property
    def device_info(self):
        """Return device information about this entity."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.config_entry.entry_id)},
            "name": "Thunderboard Integration",
            "manufacturer": "Thunderboard Team",
            "model": "Thunderboard Bot",
            "sw_version": "1.0.3",
        }

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()


class ThunderboardCurrentChannel(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        """Initialize the current channel sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"thunderboard_current_channel"
        self._attr_name = "Thunderboard Current Channel"

    @property
    def state(self):
        """Return the current channel."""
        return self.coordinator.data.get("currentChannel")

    @property
    def device_info(self):
        """Return device information about this entity."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.config_entry.entry_id)},
            "name": "Thunderboard Integration",
            "manufacturer": "Thunderboard Team",
            "model": "Thunderboard Bot",
            "sw_version": "1.0.3",
        }

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()
