from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from custom_components.arrowhead_eci.coordinator import ArrowheadEciDataUpdateCoordinator

type EciConfigEntry = ConfigEntry[RuntimeData]

@dataclass
class RuntimeData:
    """Class to hold your data."""

    coordinator: ArrowheadEciDataUpdateCoordinator

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    hass.states.async_set("hello_state.world", "Paulus")

    return True