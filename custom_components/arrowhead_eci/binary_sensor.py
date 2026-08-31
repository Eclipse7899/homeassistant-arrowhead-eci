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

    for area_id, area in config.areas.items():
        async_add_entities(
            [
                ArrowheadAreaReadyBinarySensor(area_id, area.name, coordinator, config),
            ]
        )

    async_add_entities(
        [
            ArrowheadReadyToArmSensor(coordinator, config),
            ArrowheadBatteryFaultSensor(coordinator, config),
            ArrowheadMainsFaultSensor(coordinator, config),
            ArrowheadTamperSensor(coordinator, config),
            ArrowheadDialerFaultSensor(coordinator, config),
            ArrowheadDialerLineFaultSensor(coordinator, config),
            ArrowheadFuseFaultSensor(coordinator, config),
            ArrowheadMonitoringStationActiveSensor(coordinator, config),
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


class ArrowheadZoneBinarySensorBase(ABC, CoordinatorEntity, BinarySensorEntity):
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


class ArrowheadAreaReadyBinarySensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(
        self,
        area_id: int,
        area_name: str,
        coordinator: ArrowheadEciDataUpdateCoordinator,
        config: EciConfigModel,
    ) -> None:
        super().__init__(coordinator) # ty: ignore[invalid-argument-type]
        self._area_id = area_id
        self._area_name = area_name
        self._config = config
        self.coordinator: ArrowheadEciDataUpdateCoordinator = coordinator
        self._attr_device_info = get_device_info(config)
        self._attr_name = f"{area_name} Ready to arm"
        self._attr_unique_id = "area_{area_id}_ready_to_arm"
        self._attr_device_class = BinarySensorDeviceClass.SAFETY

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.state.areas[self._area_id].ready_to_arm


class ArrowheadZoneAlarmSensor(ArrowheadZoneBinarySensorBase):
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


class ArrowheadZoneTroubleSensor(ArrowheadZoneBinarySensorBase):
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


class ArrowheadZoneBypassedSensor(ArrowheadZoneBinarySensorBase):
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


class ArrowheadZoneRadioBatteryLowSensor(ArrowheadZoneBinarySensorBase):
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


class ArrowheadZoneClosedSensor(ArrowheadZoneBinarySensorBase):
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
        return self.coordinator.state.zones[self._zone_id].closed


class ArrowheadZoneSensorWatchAlarmSensor(ArrowheadZoneBinarySensorBase):
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


class ArrowheadZoneSuperviseAlarmSensor(ArrowheadZoneBinarySensorBase):
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


class ArrowheadReadyToArmSensor(ArrowheadZoneBinarySensorBase):
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


class ArrowheadBatteryFaultSensor(ArrowheadZoneBinarySensorBase):
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


class ArrowheadMainsFaultSensor(ArrowheadZoneBinarySensorBase):
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


class ArrowheadTamperSensor(ArrowheadZoneBinarySensorBase):
    def __init__(
        self,
        coordinator: ArrowheadEciDataUpdateCoordinator,
        config: EciConfigModel,
    ) -> None:
        super().__init__(0, "", coordinator, config)
        self._attr_name = "Tamper Fault"
        self._attr_unique_id = "tamper_fault"
        self._attr_device_info = get_device_info(config)
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.state.tamper_fault


class ArrowheadDialerFaultSensor(ArrowheadZoneBinarySensorBase):
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


class ArrowheadDialerLineFaultSensor(ArrowheadZoneBinarySensorBase):
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


class ArrowheadFuseFaultSensor(ArrowheadZoneBinarySensorBase):
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


class ArrowheadMonitoringStationActiveSensor(ArrowheadZoneBinarySensorBase):
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
