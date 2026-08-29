from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from arrowhead_alarm import LoginCredentials, Mode2Client, PanelVersion
from arrowhead_alarm.exceptions import AuthError
from arrowhead_alarm.protocol.defaults import DEFAULT_MAX_AREAS, DEFAULT_MAX_ZONES
from arrowhead_alarm.protocol.exceptions import ProtocolError
from homeassistant.config_entries import (
    ConfigFlow,
    ConfigFlowResult,
)
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
)
from homeassistant.helpers.selector import NumberSelector, NumberSelectorConfig, NumberSelectorMode

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST, description={"suggested_value": "10.10.10.1"}): cv.string,
    vol.Required(CONF_PORT, description={"suggested_value": 9000}): cv.port,
    vol.Optional(CONF_USERNAME, description={"suggested_value": "admin"}): cv.string,
    vol.Optional(CONF_PASSWORD): cv.string,
    vol.Required("max_areas", description={"suggested_value": DEFAULT_MAX_AREAS}): NumberSelector(
        NumberSelectorConfig(
            min=1,
            max=DEFAULT_MAX_AREAS,
            step=1,
            mode=NumberSelectorMode.SLIDER,
        )
    ),
    vol.Required("max_zones", description={"suggested_value": DEFAULT_MAX_ZONES}): NumberSelector(
        NumberSelectorConfig(
            min=1,
            max=DEFAULT_MAX_ZONES,
            step=1,
            mode=NumberSelectorMode.SLIDER,
        )
    ),
})


@dataclass
class UserStepData:
    host: str
    port: int
    serial_number: str
    credentials: LoginCredentials | None
    max_areas: int
    max_zones: int

@dataclass
class AreaConfig:
    name: str
    enabled: bool

@dataclass
class AreasStepData(UserStepData):
    areas: dict[int, AreaConfig]

FlowConfig = UserStepData | AreasStepData | None

async def validate_input(host, port, credentials: LoginCredentials | None) -> PanelVersion:
    client = Mode2Client(host, port, credentials)
    await client.connect()
    version = await client.query_version()
    await client.disconnect()
    return version

class ArrowheadEciConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1
    _input_data: dict[str, Any]

    def __init__(self) -> None:
        self.__flow_config: FlowConfig = None

    @staticmethod
    def _get_credentials(
        username: str | None,
        password: str | None
    ) -> LoginCredentials | None:
        if username is None or password is None:
            return None

        return LoginCredentials(username, password)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            host: str | None = user_input.get(CONF_HOST)
            port: int | None = user_input.get(CONF_PORT)

            username: str | None = user_input.get(CONF_USERNAME)
            password: str | None = user_input.get(CONF_PASSWORD)

            max_areas: float | None = user_input.get("max_areas")
            max_zones: float | None = user_input.get("max_zones")

            if not host or not port:
                errors["base"] = "missing_host_port"

            elif max_areas is None or max_zones is None:
                errors["base"] = "missing_max_areas_zones"

            elif (username is None) != (password is None):
                if username is None:
                    errors["base"] = "missing_username"
                else:
                    errors["base"] = "missing_password"

            else:
                try:
                    login_credentials = self._get_credentials(username, password)

                    version = await validate_input(host, port, login_credentials)
                except AuthError:
                    errors["base"] = "invalid_auth"
                except ProtocolError:
                    errors["base"] = "invalid_protocol"
                except TimeoutError:
                    errors["base"] = "timeout"
                except Exception:
                    _LOGGER.exception("Unexpected exception")
                    errors["base"] = "unknown"
                else:
                    await self.async_set_unique_id(version.serial_number)
                    self._abort_if_unique_id_configured()
                    self.__flow_config = UserStepData(
                        host,
                        port,
                        version.serial_number,
                        login_credentials,
                        int(max_areas),
                        int(max_zones)
                    )
                    return await self.async_step_config_areas()

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_config_areas(
        self,
        user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None and isinstance(self.__flow_config, UserStepData):
            areas = {
                area_id: AreaConfig(
                    name=user_input[f"area_{area_id}_name"],
                    enabled=user_input[f"area_{area_id}_enabled"],
                )
                for area_id in range(1, self.__flow_config.max_areas + 1)
            }

            self.__flow_config = AreasStepData(
                host=self.__flow_config.host,
                port=self.__flow_config.port,
                serial_number=self.__flow_config.serial_number,
                credentials=self.__flow_config.credentials,
                max_areas=self.__flow_config.max_areas,
                max_zones=self.__flow_config.max_zones,
                areas=areas
            )
            return await self.async_step_config_zones()

        schema_dict = {}
        max_areas = self.__flow_config.max_areas if isinstance(self.__flow_config, UserStepData) else DEFAULT_MAX_AREAS
        for area_id in range(1, max_areas + 1):
            schema_dict[vol.Required(f"area_{area_id}_enabled", default=True)] = cv.boolean
            schema_dict[vol.Required(f"area_{area_id}_name", default=f"Area {area_id}")] = cv.string

        return self.async_show_form(
            step_id="config_areas",
            data_schema=vol.Schema(schema_dict),
            errors={},
        )

    async def async_step_config_zones(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:

        if user_input is not None and isinstance(self.__flow_config, AreasStepData):
            return self.async_create_entry(
                title=f"Arrowhead Alarm {self.__flow_config.serial_number}",
                data={
                    "host": self.__flow_config.host,
                    "port": self.__flow_config.port,
                    "serial_number": self.__flow_config.serial_number,
                    "username":
                        self.__flow_config.credentials.username
                        if self.__flow_config.credentials else None,
                    "password":
                        self.__flow_config.credentials.password
                        if self.__flow_config.credentials else None,
                    "areas": {
                        area_id: {
                            "name": area.name,
                            "enabled": area.enabled,
                        }
                        for area_id, area in self.__flow_config.areas.items()
                    },
                    "zones": {
                        zone_id: {
                            "name": user_input[f"zone_{zone_id}_name"],
                            "enabled": user_input[f"zone_{zone_id}_enabled"],
                        }
                        for zone_id in range(1, self.__flow_config.max_zones + 1)
                    }
                },
            )

        schema_dict = {}
        max_zones = self.__flow_config.max_zones \
            if isinstance(self.__flow_config, AreasStepData) \
            else DEFAULT_MAX_ZONES
        for zone_id in range(1, max_zones + 1):
            schema_dict[vol.Required(f"zone_{zone_id}_name", default=f"Zone {zone_id}")] = cv.string
            schema_dict[vol.Required(f"zone_{zone_id}_enabled", default=True)] = cv.boolean

        return self.async_show_form(
            step_id="config_zones",
            data_schema=vol.Schema(schema_dict),
            errors={},
        )
