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


class ArrowheadBinarySensorBase(ABC, CoordinatorEntity, BinarySensorEntity):
    def __init__(
        self,
        zone_id: int,
        zone_name: str,
        coordinator: ArrowheadEciDataUpdateCoordinator,
        config: EciConfigModel
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
