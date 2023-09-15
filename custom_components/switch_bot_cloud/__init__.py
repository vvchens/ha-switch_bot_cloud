from homeassistant.const import (
    EVENT_HOMEASSISTANT_START,
    EVENT_HOMEASSISTANT_STOP,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .send_request import request

DOMAIN = "switch_bot_cloud"
PLATFORMS = [
    Platform.COVER,
]


def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    return True


class SwitchBotCloud:
    def __init__(self, token, key):
        self._TOKEN = token
        self._KEY = key

    def send_command(self, device_id: str, command: str, parameter="default"):
        # print("device_id: " + device_id + " command: " + command + ", parameter: " + parameter)
        return request(self._TOKEN, self._KEY, "/v1.1/devices/" + device_id + "/commands", {"commandType": "command", "command": command, "parameter": parameter}, "POST")


    def fetch_status(self, device_id):
        return request(self._TOKEN, self._KEY, "/v1.1/devices/" + device_id + "/status", {}, "GET")


    def fetch_devices(self):
        return request(self._TOKEN, self._KEY, "/v1.1/devices", {}, "GET")
