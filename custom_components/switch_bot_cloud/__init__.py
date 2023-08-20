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

_LOGGER = logging.getLogger(DOMAIN)

_TOKEN = ""
_SECRET = ""

def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    return True


def send_command(device_id, command, parameter="default"):
    return request(_TOKEN, _SECRET, "/v1.1/devices/" + device_id + "/commands", {"commandType": "command", "command": command, "parameter": parameter}, "POST")


def fetch_status(device_id):
    return request(_TOKEN, _SECRET, "/v1.1/devices/" + device_id + "/status", {}, "GET")


def fetch_devices(token, secret):
    return request(_TOKEN, _SECRET, "/v1.1/devices", {}, "GET")

def set_token_and_secret(token, secret):
    _TOKEN = token
    _SECRET = secret

def logging():
    return _LOGGER
