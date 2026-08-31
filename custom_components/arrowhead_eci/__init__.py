from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from custom_components.arrowhead_eci.coordinator import ArrowheadEciDataUpdateCoordinator
from custom_components.arrowhead_eci.models import EciConfigModel

type EciConfigEntry = ConfigEntry[RuntimeData]


@dataclass
class RuntimeData:
    """Class to hold your data."""

    coordinator: ArrowheadEciDataUpdateCoordinator


PLATFORMS: list[Platform] = [
    Platform.ALARM_CONTROL_PANEL,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
    Platform.SENSOR,
]


async def async_setup_entry(hass: HomeAssistant, config_entry: EciConfigEntry) -> bool:
    config = EciConfigModel(**config_entry.data)

    coord = ArrowheadEciDataUpdateCoordinator(hass, config)

    await coord.connect()
    await coord.async_config_entry_first_refresh()

    config_entry.async_on_unload(config_entry.add_update_listener(_async_update_listener))

    config_entry.runtime_data = RuntimeData(coord)

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True


async def _async_update_listener(hass: HomeAssistant, config_entry: EciConfigEntry):
    """Handle config options update."""
    # Reload the integration when the options change.
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, config_entry: EciConfigEntry) -> bool:
    """Unload a config entry."""
    # This is called when you remove your integration or shutdown HA.
    # If you have created any custom services, they need to be removed here too.

    # Unload platforms and return result
    coord = config_entry.runtime_data.coordinator
    await coord._client.disconnect()
    return await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)
