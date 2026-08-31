from abc import ABC

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import EciConfigEntry
from .coordinator import ArrowheadEciDataUpdateCoordinator
from .models import EciConfigModel
from .util import get_device_info


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: EciConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    config = EciConfigModel(**config_entry.data)
    coordinator = config_entry.runtime_data.coordinator

    for zone_id, zone in config.zones.items():
        async_add_entities(
            [
                ArrowheadZoneAlarmSensor(zone_id, zone.name, coordinator, config),
                ArrowheadZoneTroubleSensor(zone_id, zone.name, coordinator, config),
                ArrowheadZoneBypassedSensor(zone_id, zone.name, coordinator, config),
                ArrowheadZoneRadioBatteryLowSensor(zone_id, zone.name, coordinator, config),
                ArrowheadZoneClosedSensor(zone_id, zone.name, coordinator, config),
                ArrowheadZoneSensorWatchAlarmSensor(zone_id, zone.name, coordinator, config),
            ]
        )

    for output_id, output in config.outputs.items():
        if not output.manual_control:
            async_add_entities(
                [
                    ArrowheadOutputBinarySensor(output_id, output.name, coordinator, config),
                ]
            )

    async_add_entities(
        [
            ArrowheadReadyToArmSensor(coordinator, config),
            ArrowheadBatteryFaultSensor(coordinator, config),
            ArrowheadMainsFaultSensor(coordinator, config),
            ArrowheadTamperAlarmTriggeredSensor(coordinator, config),
            ArrowheadLineFaultSensor(coordinator, config),
            ArrowheadDialerFaultSensor(coordinator, config),
            ArrowheadDialerLineFaultSensor(coordinator, config),
            ArrowheadFuseFaultSensor(coordinator, config),
            ArrowheadMonitoringStationActiveSensor(coordinator, config),
            ArrowheadDialerActiveSensor(coordinator, config),
            ArrowheadCodeTamperSensor(coordinator, config),
        ]
    )

class ArrowheadOutputBinarySensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(
        self,
        output_id: int,
        output_name: str,
        coordinator: ArrowheadEciDataUpdateCoordinator,
        config: EciConfigModel,
    ) -> None:
        super().__init__(coordinator)  # ty: ignore[invalid-argument-type]
        self._output_id = output_id
        self._output_name = output_name
        self._config = config
        self.coordinator: ArrowheadEciDataUpdateCoordinator = coordinator
        self._attr_device_info = get_device_info(config)
        self._attr_name = f"Output {output_name}"
        self._attr_unique_id = f"output_{output_id}"
        self._attr_device_class = BinarySensorDeviceClass.POWER
        self._attr_icon = "mdi:toggle-switch-variant"

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.state.outputs[self._output_id].on

class ArrowheadBinarySensorBase(ABC, CoordinatorEntity, BinarySensorEntity):
    def __init__(
        self,
        zone_id: int,
        zone_name: str,
        coordinator: ArrowheadEciDataUpdateCoordinator,
        config: EciConfigModel,
    ) -> None:
        super().__init__(coordinator)  # ty: ignore[invalid-argument-type]
        self._zone_id = zone_id
        self._zone_name = zone_name
        self._config = config
        self.coordinator: ArrowheadEciDataUpdateCoordinator = coordinator
        self._attr_device_info = get_device_info(config)


class ArrowheadZoneAlarmSensor(ArrowheadBinarySensorBase):
    def __init__(
        self,
        zone_id: int,
        zone_name: str,
        coordinator: ArrowheadEciDataUpdateCoordinator,
        config: EciConfigModel,
    ) -> None:
        super().__init__(zone_id, zone_name, coordinator, config)
        self._attr_name = f"Zone {zone_name} Alarm"
        self._attr_unique_id = f"zone_{zone_id}_alarm"
        self._attr_device_info = get_device_info(config)
        self._attr_device_class = BinarySensorDeviceClass.SAFETY

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.state.zones[self._zone_id].alarm


class ArrowheadZoneTroubleSensor(ArrowheadBinarySensorBase):
    def __init__(
        self,
        zone_id: int,
        zone_name: str,
        coordinator: ArrowheadEciDataUpdateCoordinator,
        config: EciConfigModel,
    ) -> None:
        super().__init__(zone_id, zone_name, coordinator, config)
        self._attr_name = f"Zone {zone_name} Trouble"
        self._attr_unique_id = f"zone_{zone_id}_trouble"
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.state.zones[self._zone_id].trouble_alarm


class ArrowheadZoneBypassedSensor(ArrowheadBinarySensorBase):
    def __init__(
        self,
        zone_id: int,
        zone_name: str,
        coordinator: ArrowheadEciDataUpdateCoordinator,
        config: EciConfigModel,
    ) -> None:
        super().__init__(zone_id, zone_name, coordinator, config)
        self._attr_name = f"Zone {zone_name} Bypassed"
        self._attr_unique_id = f"zone_{zone_id}_bypassed"

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.state.zones[self._zone_id].bypassed


class ArrowheadZoneRadioBatteryLowSensor(ArrowheadBinarySensorBase):
    def __init__(
        self,
        zone_id: int,
        zone_name: str,
        coordinator: ArrowheadEciDataUpdateCoordinator,
        config: EciConfigModel,
    ) -> None:
        super().__init__(zone_id, zone_name, coordinator, config)
        self._attr_name = f"Zone {zone_name} Radio Battery Low"
        self._attr_unique_id = f"zone_{zone_id}_radio_battery_low"
        self._attr_device_class = BinarySensorDeviceClass.BATTERY

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.state.zones[self._zone_id].radio_battery_low


class ArrowheadZoneClosedSensor(ArrowheadBinarySensorBase):
    def __init__(
        self,
        zone_id: int,
        zone_name: str,
        coordinator: ArrowheadEciDataUpdateCoordinator,
        config: EciConfigModel,
    ) -> None:
        super().__init__(zone_id, zone_name, coordinator, config)
        self._attr_name = f"Zone {zone_name} Closed"
        self._attr_unique_id = f"zone_{zone_id}_closed"
        self._attr_device_class = BinarySensorDeviceClass.OPENING

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.state.zones[self._zone_id].zone_closed


class ArrowheadZoneSensorWatchAlarmSensor(ArrowheadBinarySensorBase):
    def __init__(
        self,
        zone_id: int,
        zone_name: str,
        coordinator: ArrowheadEciDataUpdateCoordinator,
        config: EciConfigModel,
    ) -> None:
        super().__init__(zone_id, zone_name, coordinator, config)
        self._attr_name = f"Zone {zone_name} Sensor Watch Alarm"
        self._attr_unique_id = f"zone_{zone_id}_sensor_watch_alarm"
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.state.zones[self._zone_id].sensor_watch_alarm


class ArrowheadZoneSuperviseAlarmSensor(ArrowheadBinarySensorBase):
    def __init__(
        self,
        zone_id: int,
        zone_name: str,
        coordinator: ArrowheadEciDataUpdateCoordinator,
        config: EciConfigModel,
    ) -> None:
        super().__init__(zone_id, zone_name, coordinator, config)
        self._attr_name = f"Zone {zone_name} Supervise Alarm"
        self._attr_unique_id = f"zone_{zone_id}_supervise_alarm"
        self._attr_device_info = get_device_info(config)
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.state.zones[self._zone_id].supervise_alarm

class ArrowheadReadyToArmSensor(ArrowheadBinarySensorBase):
    def __init__(
        self,
        coordinator: ArrowheadEciDataUpdateCoordinator,
        config: EciConfigModel,
    ) -> None:
        super().__init__(0, "", coordinator, config)
        self._attr_name = "Ready to Arm"
        self._attr_unique_id = "ready_to_arm"
        self._attr_device_info = get_device_info(config)

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.state.ready_to_arm


class ArrowheadBatteryFaultSensor(ArrowheadBinarySensorBase):
    def __init__(
        self,
        coordinator: ArrowheadEciDataUpdateCoordinator,
        config: EciConfigModel,
    ) -> None:
        super().__init__(0, "", coordinator, config)
        self._attr_name = "Battery Fault"
        self._attr_unique_id = "battery_fault"
        self._attr_device_info = get_device_info(config)
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.state.battery_fault


class ArrowheadMainsFaultSensor(ArrowheadBinarySensorBase):
    def __init__(
        self,
        coordinator: ArrowheadEciDataUpdateCoordinator,
        config: EciConfigModel,
    ) -> None:
        super().__init__(0, "", coordinator, config)
        self._attr_name = "Mains Fault"
        self._attr_unique_id = "mains_fault"
        self._attr_device_info = get_device_info(config)
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.state.mains_fault


class ArrowheadTamperAlarmTriggeredSensor(ArrowheadBinarySensorBase):
    def __init__(
        self,
        coordinator: ArrowheadEciDataUpdateCoordinator,
        config: EciConfigModel,
    ) -> None:
        super().__init__(0, "", coordinator, config)
        self._attr_name = "Tamper Alarm Triggered"
        self._attr_unique_id = "tamper_alarm_triggered"
        self._attr_device_info = get_device_info(config)
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.state.tamper_alarm_triggered


class ArrowheadLineFaultSensor(ArrowheadBinarySensorBase):
    def __init__(
        self,
        coordinator: ArrowheadEciDataUpdateCoordinator,
        config: EciConfigModel,
    ) -> None:
        super().__init__(0, "", coordinator, config)
        self._attr_name = "Line Fault"
        self._attr_unique_id = "line_fault"
        self._attr_device_info = get_device_info(config)
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.state.line_fault


class ArrowheadDialerFaultSensor(ArrowheadBinarySensorBase):
    def __init__(
        self,
        coordinator: ArrowheadEciDataUpdateCoordinator,
        config: EciConfigModel,
    ) -> None:
        super().__init__(0, "", coordinator, config)
        self._attr_name = "Dialer Fault"
        self._attr_unique_id = "dialer_fault"
        self._attr_device_info = get_device_info(config)
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.state.dialer_fault


class ArrowheadDialerLineFaultSensor(ArrowheadBinarySensorBase):
    def __init__(
        self,
        coordinator: ArrowheadEciDataUpdateCoordinator,
        config: EciConfigModel,
    ) -> None:
        super().__init__(0, "", coordinator, config)
        self._attr_name = "Dialer Line Fault"
        self._attr_unique_id = "dialer_line_fault"
        self._attr_device_info = get_device_info(config)
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.state.dialer_line_fault


class ArrowheadFuseFaultSensor(ArrowheadBinarySensorBase):
    def __init__(
        self,
        coordinator: ArrowheadEciDataUpdateCoordinator,
        config: EciConfigModel,
    ) -> None:
        super().__init__(0, "", coordinator, config)
        self._attr_name = "Fuse Fault"
        self._attr_unique_id = "fuse_fault"
        self._attr_device_info = get_device_info(config)
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.state.fuse_fault


class ArrowheadMonitoringStationActiveSensor(ArrowheadBinarySensorBase):
    def __init__(
        self,
        coordinator: ArrowheadEciDataUpdateCoordinator,
        config: EciConfigModel,
    ) -> None:
        super().__init__(0, "", coordinator, config)
        self._attr_name = "Monitoring Station Active"
        self._attr_unique_id = "monitoring_station_active"
        self._attr_device_info = get_device_info(config)
        self._attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.state.monitoring_station_active


class ArrowheadDialerActiveSensor(ArrowheadBinarySensorBase):
    def __init__(
        self,
        coordinator: ArrowheadEciDataUpdateCoordinator,
        config: EciConfigModel,
    ) -> None:
        super().__init__(0, "", coordinator, config)
        self._attr_name = "Dialer Active"
        self._attr_unique_id = "dialer_active"
        self._attr_device_info = get_device_info(config)
        self._attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.state.dialer_active


class ArrowheadCodeTamperSensor(ArrowheadBinarySensorBase):
    def __init__(
        self,
        coordinator: ArrowheadEciDataUpdateCoordinator,
        config: EciConfigModel,
    ) -> None:
        super().__init__(0, "", coordinator, config)
        self._attr_name = "Tamper Sensor"
        self._attr_unique_id = "tamper_sensor"
        self._attr_device_info = get_device_info(config)
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.state.code_tamper