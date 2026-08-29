"""Arrowhead Alarm Panel alarm control panel platform."""

import logging

from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
    AlarmControlPanelEntityFeature,
    AlarmControlPanelState,
    CodeFormat,
)
from homeassistant.core import DOMAIN, HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.arrowhead_eci import EciConfigEntry

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: EciConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = config_entry.runtime_data.coordinator

    async_add_entities([ArrowheadAlarmControlPanel(coordinator, config_entry, panel_config)])


class ArrowheadAlarmControlPanel(CoordinatorEntity, AlarmControlPanelEntity):
    """Representation of an Arrowhead Alarm Panel."""

    def __init__(
        self,
        coordinator: ArrowheadDataUpdateCoordinator,
        config_entry: EciConfigEntry,
        panel_config: dict[str, Any],
    ) -> None:
        """Initialize the alarm control panel."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._panel_config = panel_config
        self._attr_name = f"Arrowhead {panel_config['name']}"
        self._attr_unique_id = f"{config_entry.entry_id}_alarm_panel"

        # Set supported features based on panel capabilities
        self._attr_supported_features = (
            AlarmControlPanelEntityFeature.ARM_AWAY | AlarmControlPanelEntityFeature.ARM_HOME
        )

        # Set code format - no code required since PIN is configured
        self._attr_code_format = CodeFormat.NUMBER
        self._attr_code_arm_required = False  # PIN already configured in client

        # Set device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": f"Arrowhead {panel_config['name']}",
            "manufacturer": "Arrowhead Alarm Products",
            "model": panel_config["name"],
            "sw_version": self.coordinator.data.get("firmware_version")
            if self.coordinator.data
            else None,
        }

    @property
    def alarm_state(self) -> AlarmControlPanelState:
        """Return the state of the alarm control panel using new enum."""
        if not self.coordinator.data:
            return AlarmControlPanelState.DISARMED

        data = self.coordinator.data

        # Check for alarm condition first
        if data.get("alarm", False):
            return AlarmControlPanelState.TRIGGERED

        # Check for arming/pending state
        if data.get("arming", False):
            return AlarmControlPanelState.PENDING

        # Check armed states
        if data.get("armed", False):
            if data.get("stay_mode", False):
                return AlarmControlPanelState.ARMED_HOME
            else:
                return AlarmControlPanelState.ARMED_AWAY

        return AlarmControlPanelState.DISARMED

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return (
            self.coordinator.last_update_success
            and self.coordinator.data is not None
            and self.coordinator.data.get("connection_state") == "connected"
        )

    async def disarm(self, code: Optional[str] = None) -> None:
        """Send disarm command."""
        _LOGGER.info("Disarming %s", self._attr_name)
        success = await self.coordinator.async_disarm()

        if not success:
            _LOGGER.error("Failed to disarm %s", self._attr_name)

    async def async_alarm_arm_away(self, code: Optional[str] = None) -> None:
        """Send arm away command."""
        _LOGGER.info("Arming %s (away mode)", self._attr_name)
        success = await self.coordinator.async_arm_away()

        if not success:
            _LOGGER.error("Failed to arm %s (away mode)", self._attr_name)

    async def async_alarm_arm_home(self, code: Optional[str] = None) -> None:
        """Send arm home command."""
        _LOGGER.info("Arming %s (stay mode)", self._attr_name)

        # Add debug logging to see what's happening
        _LOGGER.debug(
            "Coordinator data before arm_stay: %s",
            list(self.coordinator.data.keys()) if self.coordinator.data else "No data",
        )
        _LOGGER.debug("Client connection state: %s", self.coordinator.client.is_connected)

        success = await self.coordinator.async_arm_stay()

        if success:
            _LOGGER.info("Successfully armed %s in stay mode", self._attr_name)
        else:
            _LOGGER.error("Failed to arm %s (stay mode)", self._attr_name)
            # Add additional debugging
            _LOGGER.debug(
                "Coordinator data after failed arm_stay: %s",
                list(self.coordinator.data.keys()) if self.coordinator.data else "No data",
            )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()
