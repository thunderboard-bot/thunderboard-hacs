from datetime import timedelta
from logging import Logger, getLogger
from typing import Final

from homeassistant.const import Platform

LOGGER: Logger = getLogger(__package__)

COORDINATOR_UPDATE_INTERVAL: timedelta = timedelta(seconds=30)

DOMAIN = "thunderboard"
PLATFORMS: Final = [Platform.BUTTON]