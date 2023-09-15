from __future__ import annotations

import voluptuous as vol

from homeassistant.components.media_player import PLATFORM_SCHEMA, MediaPlayerEntity, MediaPlayerEntityFeature, MediaPlayerDeviceClass, MediaPlayerState
from homeassistant.const import CONF_API_TOKEN, CONF_API_KEY, CONF_NAME, CONF_DEVICE_ID, CONF_UNIQUE_ID
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.reload import setup_reload_service
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from . import DOMAIN, PLATFORMS, SwitchBotCloud

CONF_IR_CONTROL = 'ir_control'

_MEDIA_PLAYERS_SCHEMA = vol.All(
    cv.ensure_list,
    [
        vol.Schema(
            {
                CONF_NAME: cv.string,
                CONF_DEVICE_ID: cv.string,
                CONF_UNIQUE_ID: cv.string,
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
        vol.Required(CONF_IR_CONTROL): _MEDIA_PLAYERS_SCHEMA,
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

    ir_control = []
    ir_control_conf = config[CONF_IR_CONTROL]

    for conf in ir_control_conf:
        ir_control.append(
            SwitchBotCloudMediaPlayer(
                conf[CONF_NAME],
                conf[CONF_DEVICE_ID],
                conf.get(CONF_UNIQUE_ID),
                cloud,
            )
        )
    add_entities(ir_control)


class SwitchBotCloudMediaPlayer(MediaPlayerEntity, RestoreEntity):

    def __init__(
        self,
        name: str,
        device_id: str,

        unique_id: str,
        cloud: SwitchBotCloud,
    ):
        """Initialize the IR controller."""
        self._cloud = cloud
        self._attr_name = name
        self._attr_unique_id = unique_id
        self._device_id = device_id
        self._attr_device_class = MediaPlayerDeviceClass.TV
        self._attr_supported_features = (MediaPlayerEntityFeature.TURN_ON | MediaPlayerEntityFeature.TURN_OFF | MediaPlayerEntityFeature.VOLUME_MUTE)
 
    def turn_on(self) -> None:
        """Turn the media player on."""
        if self.state == MediaPlayerState.OFF:
            self._cloud.send_command(self._device_id, "turnOn")
            self._attr_state = MediaPlayerState.ON

    def turn_off(self) -> None:
        """Turn the media player off."""
        if self.state == MediaPlayerState.ON:
            self._cloud.send_command(self._device_id, "turnOff")
            self._attr_state = MediaPlayerState.OFF

    def mute_volume(self, mute: bool) -> None:
        """Mute the volume."""
        self._cloud.send_command(self._device_id, "setMute", "mute" if mute else "unmute")
