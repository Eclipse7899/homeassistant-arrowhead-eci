"""Data update coordinator for Arrowhead Alarm Panel."""
import logging
from enum import Enum

from arrowhead_alarm import ArmingMode, LoginCredentials, Mode2Client, PanelState
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class ConnectionState(Enum):
    """Represents the connection state."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"


class ArrowheadEciDataUpdateCoordinator(DataUpdateCoordinator[PanelState]):
    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=None,
        )
        self.host = config_entry.data[CONF_HOST]
        self.port = config_entry.data[CONF_PORT]
        self.user = config_entry.data[CONF_USERNAME]
        self.pwd = config_entry.data[CONF_PASSWORD]
        
        if self.user is None or self.pwd is None:
            creds = None
        else:
            creds = LoginCredentials(self.user, self.pwd)

        self._client = Mode2Client(host=self.host, port=self.port, credentials=creds)
        self._client.state_publisher.subscribe(self.async_set_updated_data)

    async def disarm(self, area: int, pin: int):
        """Disarm the alarm."""
        await self._client.disarm(area, pin)
        
    async def arm_stay(self, area: int):
        """Arm the alarm in stay mode."""
        await self._client.arm_area(area, ArmingMode.STAY)
        
    async def arm_away(self, area: int):
        """Arm the alarm in away mode."""
        await self._client.arm_area(area, ArmingMode.AWAY)
