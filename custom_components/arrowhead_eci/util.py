from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN
from .models import EciConfigModel


def get_device_info(config: EciConfigModel):
    return DeviceInfo(
        identifiers={(DOMAIN, f"eci_alarm_{config.serial_number}")},
        manufacturer="Arrowhead Alarm Products",
        name=f"Eci Alarm Panel - {config.serial_number}",
        serial_number=config.serial_number,
    )
