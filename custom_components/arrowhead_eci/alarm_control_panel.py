"""Arrowhead Alarm Panel alarm control panel platform."""
import logging
from typing import override

from arrowhead_alarm import AlarmState
from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
    AlarmControlPanelEntityFeature,
    AlarmControlPanelState,
    CodeFormat,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import UndefinedType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.arrowhead_eci import ArrowheadEciDataUpdateCoordinator, EciConfigEntry

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: EciConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = config_entry.runtime_data.coordinator
    
    area_control_panels = [
        ArrowheadAlarmAreaControlPanel(area_id, area["enabled"], coordinator, config_entry)
        for area_id, area in config_entry.data["areas"].items()
    ]

    async_add_entities(area_control_panels)


class ArrowheadAlarmAreaControlPanel(CoordinatorEntity, AlarmControlPanelEntity):
    """Representation of an Arrowhead Alarm Panel."""

    def __init__(
        self,
        area_id: int,
        is_enabled: bool,
        coordinator: ArrowheadEciDataUpdateCoordinator,
        config_entry: EciConfigEntry,
    ) -> None:
        """Initialize the alarm control panel."""
        super().__init__(coordinator)  # ty: ignore[invalid-argument-type]
        self.area_id = area_id
        self.is_enabled = is_enabled
        self.coordinator: ArrowheadEciDataUpdateCoordinator = coordinator
        self.config_entry = config_entry

    def device_info(self) -> DeviceInfo | None:
        return DeviceInfo(
            name=f"Alarm Panel - AreaConfigModel {self.area_id}",
            identifiers={(DOMAIN, f"area_{self.area_id}"
                                  f"-{self.config_entry.data['serial_number']}")},
            manufacturer="Arrowhead Alarm Products",
        )

    @override
    def enabled(self) -> bool:
        """Return whether the area is enabled."""
        return self.is_enabled
    
    @override
    def name(self) -> str | UndefinedType | None:
        return f"Arrowhead Alarm AreaConfigModel {self.area_id}"

    @override
    def code_format(self) -> CodeFormat | None:
        """Return the code format."""
        return CodeFormat.NUMBER
    
    @override
    def code_arm_required(self) -> bool:
        """Whether the code is required for arm actions."""
        return False

    @override
    def supported_features(self) -> AlarmControlPanelEntityFeature:
        """Return the list of supported features."""
        return AlarmControlPanelEntityFeature.ARM_AWAY | AlarmControlPanelEntityFeature.ARM_HOME

    @property
    def alarm_state(self) -> AlarmControlPanelState:
        """Return the state of the alarm control panel."""
        area = self.coordinator.state.areas.get(self.area_id)

        if area is None:
            return AlarmControlPanelState.DISARMED

        match area.state:
            case AlarmState.DISARMED:
                return AlarmControlPanelState.DISARMED
            case AlarmState.ARMED_STAY:
                return AlarmControlPanelState.ARMED_HOME
            case AlarmState.ARMED_AWAY:
                return AlarmControlPanelState.ARMED_AWAY
            case AlarmState.ALARM_TRIGGERED:
                return AlarmControlPanelState.TRIGGERED
            case AlarmState.ARMING_AWAY:
                return AlarmControlPanelState.ARMING
            case AlarmState.ARMING_STAY:
                return AlarmControlPanelState.ARMING
            case _:
                return AlarmControlPanelState.DISARMED


    @callback
    def _handle_coordinator_update(self) -> None:
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        return True

    async def async_alarm_disarm(self, code: str | None = None) -> None:
        """Send disarm command."""
        if code is None:
            raise HomeAssistantError("Code is required for disarming the alarm")
        try:
            int_code = int(code)
        except ValueError as e:
            raise HomeAssistantError("Invalid code format. Only numbers are allowed.") from e
        await self.coordinator.disarm(self.area_id, int_code)

    async def async_alarm_arm_home(self, code: str | None = None) -> None:
        """Send arm home command."""
        await self.coordinator.arm_stay(self.area_id)

    async def async_alarm_arm_away(self, code: str | None = None) -> None:
        """Send arm away command."""
        await self.coordinator.arm_away(self.area_id)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()
