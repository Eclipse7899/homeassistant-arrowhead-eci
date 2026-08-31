"""Data update coordinator for Arrowhead Alarm Panel."""
import logging
from enum import Enum
from typing import TypedDict

from arrowhead_alarm import ArmingMode, LoginCredentials, Mode2Client, PanelState
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from .models import EciConfigModel

_LOGGER = logging.getLogger(__name__)


class ConnectionState(Enum):
    """Represents the connection state."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"

class EciRuntimeData(TypedDict):
    """Class to hold your data."""
    panel_state: PanelState

class ArrowheadEciDataUpdateCoordinator(DataUpdateCoordinator[EciRuntimeData]):
    def __init__(self, hass: HomeAssistant, config: EciConfigModel):
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=None,
        )
        self.host = config.host
        self.port = config.port
        self.user = config.username
        self.pwd = config.password

        if self.user is None or self.pwd is None:
            creds = None
        else:
            creds = LoginCredentials(self.user, self.pwd)

        self._client = Mode2Client(host=self.host, port=self.port, credentials=creds)
        self._client.state_publisher.subscribe(self._on_panel_state_update)
        self.state = self._client.state

    async def connect(self):
        await self._client.connect()

    async def _async_update_data(self):
        return self.state

    def _on_panel_state_update(self, state: PanelState):
        self.state = state
        self.async_set_updated_data({"panel_state": state})

    async def disarm(self, area: int, pin: int):
        """Disarm the alarm."""
        await self._client.disarm(area, pin)
        
    async def arm_stay(self, area: int):
        """Arm the alarm in stay mode."""
        await self._client.arm_area(area, ArmingMode.STAY)
        
    async def arm_away(self, area: int):
        """Arm the alarm in away mode."""
        await self._client.arm_area(area, ArmingMode.AWAY)
