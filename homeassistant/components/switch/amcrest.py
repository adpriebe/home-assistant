"""
Support for toggling Amcrest IP camera settings.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/switch.amcrest/
"""
import asyncio
import logging

from homeassistant.components.amcrest import (
    DATA_AMCREST, SWITCHES)

from homeassistant.const import (
    CONF_NAME, CONF_SWITCHES, STATE_UNKNOWN, STATE_OFF, STATE_ON)
from homeassistant.helpers.entity import ToggleEntity

DEPENDENCIES = ['amcrest']

REQUIREMENTS = ['amcrest==1.2.2']
_LOGGER = logging.getLogger(__name__)


@asyncio.coroutine
def async_setup_platform(hass, config, async_add_devices, discovery_info=None):
    """Set up the IP camera switch platform."""
    if discovery_info is None:
        return

    name = discovery_info[CONF_NAME]
    switches = discovery_info[CONF_SWITCHES]
    camera = hass.data[DATA_AMCREST][name].device

    all_switches = []

    for setting in switches:
        all_switches.append(AmcrestSwitch(setting, camera))

    async_add_devices(all_switches, True)


class AmcrestSwitch(ToggleEntity):
    """An abstract class for an IP camera setting."""

    def __init__(self, setting, camera):
        """Initialize the switch."""
        self._setting = setting
        self._camera = camera
        self._name = SWITCHES[setting][0]
        self._icon = SWITCHES[setting][1]
        self._state = STATE_UNKNOWN

    @property
    def should_poll(self):
        """Poll for status regularly."""
        return True

    @property
    def name(self):
        """Return the name of the switch if any."""
        return self._name

    @property
    def state(self):
        """Return the state of the switch."""
        return self._state

    @property
    def is_on(self):
        """Return true if switch is on."""
        return self._state == STATE_ON

    def turn_on(self, **kwargs):
        """Turn setting on."""
        if self._setting == 'motion_detection':
            self._camera.motion_detection = 'true'
        elif self._setting == 'motion_recording':
            self._camera.motion_recording = 'true'
        else:
            _LOGGER.error("Can't turn on unknown setting: %s", self._setting)

    def turn_off(self, **kwargs):
        """Turn setting off."""
        if self._setting == 'motion_detection':
            self._camera.motion_detection = 'false'
        elif self._setting == 'motion_recording':
            self._camera.motion_recording = 'false'
        else:
            _LOGGER.error("Can't turn on unknown setting: %s", self._setting)

    def update(self):
        """Update setting state."""
        _LOGGER.debug("Polling state for setting: %s ", self._name)

        if self._setting == 'motion_detection':
            detection = self._camera.is_motion_detector_on()
        elif self._setting == 'motion_recording':
            detection = self._camera.is_record_on_motion_detection()
        else:
            _LOGGER.error("Can't update state for unknown setting: %s",
                          self._setting)
            self._state = STATE_UNKNOWN
            return

        self._state = STATE_ON if detection else STATE_OFF

    @property
    def icon(self):
        """Return the icon for the switch."""
        return self._icon
