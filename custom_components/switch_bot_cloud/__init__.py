import logging

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

LOGGER = logging.getLogger(DOMAIN)

_TOKEN = ""
_KEY = ""

def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    return True


def send_command(device_id, command, parameter="default"):
    print("device_id: " + device_id + " command: " + command + ", parameter: " + parameter)
    return request(_TOKEN, _KEY, "/v1.1/devices/" + device_id + "/commands", {"commandType": "command", "command": command, "parameter": parameter}, "POST")


def fetch_status(device_id):
    return request(_TOKEN, _KEY, "/v1.1/devices/" + device_id + "/status", {}, "GET")


def fetch_devices():
    return request(_TOKEN, _KEY, "/v1.1/devices", {}, "GET")

def set_token_and_key(token, key):
    _TOKEN = token
    _KEY = key
    print("token: " + _TOKEN + ", secret: " + _KEY)
