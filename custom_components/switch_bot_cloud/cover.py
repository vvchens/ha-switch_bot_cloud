from __future__ import annotations

from time import sleep
from threading import Timer

import voluptuous as vol

from homeassistant.components.cover import PLATFORM_SCHEMA, CoverEntity, ATTR_POSITION, CoverEntityFeature
from homeassistant.const import CONF_API_TOKEN, CONF_API_KEY, CONF_COVERS, CONF_NAME, CONF_DEVICE_ID, CONF_DEVICE_CLASS, CONF_UNIQUE_ID, STATE_CLOSED, STATE_CLOSING, STATE_OPEN, STATE_OPENING, STATE_UNKNOWN
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.reload import setup_reload_service
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from . import DOMAIN, PLATFORMS, SwitchBotCloud

CONF_DIRECTION_UP = 'up'
CONF_DIRECTION_DOWN = 'down'
CONF_DIRECTION = 'direction'

_COVERS_SCHEMA = vol.All(
    cv.ensure_list,
    [
        vol.Schema(
            {
                CONF_NAME: cv.string,
                CONF_DEVICE_CLASS: cv.string,
                CONF_DEVICE_ID: cv.string,
                # CONF_OPEN_PIN: cv.positive_int,
                CONF_UNIQUE_ID: cv.string,
                vol.Optional(CONF_DIRECTION, default=CONF_DIRECTION_DOWN): cv.string, # type: ignore
                # vol.Optional(CONF_INTERMEDIATE_MODE, default=DEFAULT_INTERMEDIATE_MODE): cv.boolean,
                # vol.Optional(CONF_CLOSE_DURATION, default=DEFAULT_CLOSE_DURATION): cv.positive_int,
                # vol.Optional(CONF_OPEN_DURATION, default=DEFAULT_OPEN_DURATION): cv.positive_int,
                # vol.Optional(CONF_DEVICE_CLASS, default=None): cv.string,
            }
        )
    ],
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_API_TOKEN): cv.string,
        vol.Required(CONF_API_KEY): cv.string,
        vol.Required(CONF_COVERS): _COVERS_SCHEMA,
    }
)

def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:

    setup_reload_service(hass, DOMAIN, PLATFORMS)

    cloud = SwitchBotCloud(config[CONF_API_TOKEN], config[CONF_API_KEY])

    covers = []
    covers_conf = config[CONF_COVERS]

    for cover in covers_conf:
        covers.append(
            SwitchBotCloudCover(
                cover[CONF_NAME],
                cover[CONF_DEVICE_ID],
                cover[CONF_DEVICE_CLASS],
                cover[CONF_DIRECTION],
                cover.get(CONF_UNIQUE_ID),
                cloud,
            )
        )
    add_entities(covers)


class SwitchBotCloudCover(CoverEntity, RestoreEntity):
    """Representation of a Orange GPIO cover."""

    def __init__(
        self,
        name,
        device_id,
        device_class,
        direction,

        unique_id,
        cloud,
    ):
        """Initialize the cover."""
        self._cloud = cloud
        self._attr_name = name
        self._attr_unique_id = unique_id
        self._state = STATE_UNKNOWN
        self._device_id = device_id
        self._direction = direction
        self._attr_device_class = device_class
        self._moving = False
        self._battery = -1
        self._attr_supported_features = (CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE | CoverEntityFeature.SET_POSITION)
        self._update_position()

    @property
    def is_closed(self) -> bool:
        """Return if the cover is closed."""
        return self._state == STATE_CLOSED

    @property
    def is_opening(self) -> bool:
        """Return if the cover is currently opening."""
        return self._state == STATE_OPENING

    @property
    def is_closing(self) -> bool:
        """Return if the cover is currently closing."""
        return self._state == STATE_CLOSING

    def _update_position(self):
        body = self._cloud.fetch_status(self._device_id)

        self._battery = body['battery']
        self._attr_current_cover_position = body['slidePosition'] / 2
        # self._direction = body['direction'].lower()
        if self._attr_current_cover_position == 0:
            self._state = STATE_CLOSED
        else:
            self._state = STATE_OPEN
        if 'moving' in body and body['moving'] == True:
            self._state = STATE_OPENING if self._state == STATE_OPEN else STATE_CLOSING

    def _trigger(self, command, parameter="default"):
        self._cloud.send_command(self._device_id, command, parameter)
        # while(self._state == STATE_OPENING or self._state == STATE_CLOSING): 
        #     sleep(5)
        #     self._update_position()

    def close_cover(self, **_):
        """Close the cover."""
        self._state = STATE_CLOSING
        if self._direction == CONF_DIRECTION_DOWN:
            self._trigger("closeDown")
            self._attr_current_cover_position = 0
        else:
            self._trigger("closeUp")
            self._attr_current_cover_position = 100
        self._state = STATE_CLOSED

    def open_cover(self, **_):
        """Open the cover."""
        self._state = STATE_OPENING
        self._trigger("fullyOpen")
        self._attr_current_cover_position = 50
        self._state = STATE_OPEN


    def set_cover_position(self, **kwargs):
        """Move the cover to a specific position."""
        position = kwargs[ATTR_POSITION]
        self._state = STATE_CLOSING if position == 0 or position == 100 else STATE_OPENING
        direction = "down"
        if position > 50:
            direction = "up"
            position = 100 - position
        self._trigger("setPosition", direction + ";" + str(position * 2))
        self._attr_current_cover_position = position
        self._state = STATE_CLOSED if position == 0 or position == 100 else STATE_OPEN
