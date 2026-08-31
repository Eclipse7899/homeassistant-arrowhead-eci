from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.arrowhead_eci import (
    ArrowheadEciDataUpdateCoordinator,
    EciConfigEntry,
)

from .models import EciConfigModel
from .util import get_device_info


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: EciConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    config = EciConfigModel(**config_entry.data)
    coordinator = config_entry.runtime_data.coordinator

    async_add_entities([
        ArrowheadVersionSensor(coordinator, config),
    ])


class ArrowheadVersionSensor(CoordinatorEntity, SensorEntity):
    def __init__(
        self,
        coordinator: ArrowheadEciDataUpdateCoordinator,
        config: EciConfigModel,
    ) -> None:
        super().__init__(coordinator) # ty: ignore[invalid-argument-type]

        self.coordinator: ArrowheadEciDataUpdateCoordinator = coordinator

        self._attr_device_info = get_device_info(config)
        self._attr_name = "Firmware Version"
        self._attr_unique_id = "firmware_version"
        self._attr_icon = "mdi:chip"

    @property
    def native_value(self) -> str | None:
        version = self.coordinator.version
        if version is None:
            return None

        firmware = version.firmware_version

        return f"v{firmware.major_version}.{firmware.minor_version}.{firmware.patch_version}"