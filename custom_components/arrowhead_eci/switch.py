from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.arrowhead_eci import ArrowheadEciDataUpdateCoordinator, EciConfigEntry

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
                ArrowheadZoneBypassSwitch(zone_id, zone.name, coordinator, config),
            ]
        )

    for output_id, output in config.outputs.items():
        if output.manual_control:
            async_add_entities(
                [
                    ArrowheadOutputSwitch(output_id, output.name, coordinator, config),
                ]
            )


class ArrowheadZoneBypassSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(
        self,
        zone_id: int,
        zone_name: str,
        coordinator: ArrowheadEciDataUpdateCoordinator,
        config: EciConfigModel,
    ):
        super().__init__(coordinator)  # ty: ignore[invalid-argument-type]
        self._zone_id = zone_id
        self._zone_name = zone_name
        self._config = config
        self.coordinator: ArrowheadEciDataUpdateCoordinator = coordinator

        self._attr_device_info = get_device_info(config)
        self._attr_name = f"Zone {zone_name} Bypass"
        self._attr_unique_id = f"zone_{zone_id}_bypass"
        self._attr_device_class = SwitchDeviceClass.SWITCH
        self._attr_icon = "mdi:shield-off"

    async def async_turn_on(self, **kwargs):
        """Bypass the zone."""
        await self.coordinator.bypass_zone(self._zone_id)

    async def async_turn_off(self, **kwargs):
        """Unbypass the zone."""
        await self.coordinator.unbypass_zone(self._zone_id)

    @property
    def is_on(self):
        """Return True if the zone is bypassed."""
        return self.coordinator.state.zones[self._zone_id].bypassed


class ArrowheadOutputSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(
        self,
        output_id: int,
        output_name: str,
        coordinator: ArrowheadEciDataUpdateCoordinator,
        config: EciConfigModel,
    ):
        super().__init__(coordinator)  # ty: ignore[invalid-argument-type]
        self._output_id = output_id
        self._output_name = output_name
        self._config = config
        self.coordinator: ArrowheadEciDataUpdateCoordinator = coordinator

        self._attr_device_info = get_device_info(config)
        self._attr_name = f"Output {output_name}"
        self._attr_unique_id = f"output_{output_id}"
        self._attr_device_class = SwitchDeviceClass.SWITCH
        self._attr_icon = "mdi:power-plug-off"

    async def async_turn_on(self, **kwargs):
        """Turn on the output."""
        await self.coordinator.turn_on_output(self._output_id)

    async def async_turn_off(self, **kwargs):
        """Turn off the output."""
        await self.coordinator.turn_off_output(self._output_id)

    @property
    def is_on(self):
        """Return True if the output is on."""
        return self.coordinator.state.outputs[self._output_id].on
