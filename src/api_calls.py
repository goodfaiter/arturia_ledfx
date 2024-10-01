from abc import ABC, abstractmethod
from typing import Dict
import requests


class ApiCall(ABC):
    def __init__(self, host: str):
        """Base class from API calls to LedFX.

        :param host: Host name of the LedFX to be addressed.
        """
        self._host = host

    @abstractmethod
    def process(self, midi_msg):
        """Process midi input into REST API.

        :param midi_msg: midi_msg container to process and turn into REST API.
        """
        raise NotImplementedError("Please Implement this method")


class OneShot(ApiCall):
    def __init__(self, cfg: Dict):
        """Calls oneshot API on process call.

        :param cfg: API call configurations such as virtual_id, brightness etc.
        """
        super().__init__(cfg['host'])
        self._virtual = cfg['virtual_id']
        self._api = self._host + '/api/virtuals_tools/' + self._virtual
        self._put_json = {
            "tool": "oneshot",
            "color": cfg['color'],
            "ramp": cfg['ramp'],
            "hold": cfg['hold'],
            "fade": cfg['fade'],
            "brightness": cfg['brightness']
        }

    def process(self, midi_msg):
        print(requests.put(self._api, json=self._put_json))


class Ripple(ApiCall):
    def __init__(self, cfg: Dict):
        """Calls ripple API on process call.

        :param cfg: API call configurations such as virtual_id, brightness etc.
        """
        super().__init__(cfg['host'])
        self._virtual = cfg['virtual_id']
        self._api = self._host + '/api/virtuals_tools/' + self._virtual
        self._put_json = {
            "tool": "ripple",
            "color": cfg['color'],
            "ramp": cfg['ramp'],
            "hold": cfg['hold'],
            "fade": cfg['fade'],
            "probability": cfg['probability'],
            "brightness": cfg['brightness']
        }

    def process(self, midi_msg):
        print(requests.put(self._api, json=self._put_json))


class Wave(ApiCall):
    def __init__(self, cfg: Dict):
        """Calls wave API on process call.

        :param cfg: API call configurations such as virtual_id, brightness etc.
        """
        super().__init__(cfg['host'])
        self._virtual = cfg['virtual_id']
        self._api = self._host + '/api/virtuals_tools/' + self._virtual
        self._put_json = {
            "tool": "wave",
            "color": cfg['color'],
            "timestep": cfg['timestep'],
            "pixel_step": cfg['pixel_step']
        }

    def process(self, midi_msg):
        print(requests.put(self._api, json=self._put_json))


class AdjustBrightness(ApiCall):
    def __init__(self, cfg: Dict):
        """Calls brightness adjustment API on process call.

        Note that we only process Nth process request due to too frequent process() call from midi otherwise.

        :param cfg: API call configurations such as virtual_id etc.
        """
        super().__init__(cfg['host'])
        self._virtual = cfg['virtual_id']
        self._api = self._host + '/api/virtuals/' + self._virtual + '/effects'
        self._max_control_value = 127.0

        # The knob polling frequency is too large, so we only trigger on the Nth one.
        self._counter = 1
        self._skip = 4

    def process(self, midi_msg):
        self._counter += 1
        if self._counter % self._skip == 0:
            response = requests.get(self._api)
            todo = response.json()['effect']
            todo['config']['brightness'] = midi_msg.value / self._max_control_value
            todo['config']['background_brightness'] = midi_msg.value / self._max_control_value
            requests.put(self._api, json=todo)
            self._counter = 0


class SwitchToEffect(ApiCall):
    """Calls effect adjustment API on process call.

    Note that in this case, preset is not set, and it will use the default.

    :param cfg: API call configurations such as virtual_id etc.
    """
    def __init__(self, cfg: Dict):
        super().__init__(cfg['host'])
        self._virtual = cfg['virtual_id']
        self._api = self._host + '/api/virtuals/' + self._virtual + '/effects'
        self._put_json = {
            "type": cfg['type']
        }

    def process(self, midi_msg):
        print(requests.put(self._api, json=self._put_json))


class SwitchToEffectAndPreset(ApiCall):
    """Calls effect adjustment API on process call.

    Note that in this case, we first read out current brightness and then set it to the new effect to keep it the same.

    :param cfg: API call configurations such as virtual_id etc.
    """
    def __init__(self, cfg: Dict):
        super().__init__(cfg['host'])
        self._virtual = cfg['virtual_id']
        self._api = self._host + '/api/virtuals/' + self._virtual + '/presets'
        self._brightness_api = self._host + '/api/virtuals/' + self._virtual + '/effects'
        self._put_json = {
            "category": cfg['category'],
            "effect_id": cfg['effect_id'],
            "preset_id": cfg['preset_id']
        }

    def process(self, midi_msg):
        # Get previous effect brightness
        response = requests.get(self._brightness_api)
        brightness = response.json()['effect']['config']['brightness']
        bg_brightness = response.json()['effect']['config']['background_brightness']

        # Switch to new effect and preset
        requests.put(self._api, json=self._put_json)

        # Get config of new effect
        response = requests.get(self._brightness_api)
        todo = response.json()['effect']

        # Overwrite the brightness from previous preset to keeep the brightness
        todo['config']['brightness'] = brightness
        todo['config']['background_brightness'] = bg_brightness
        requests.put(self._brightness_api, json=todo)
