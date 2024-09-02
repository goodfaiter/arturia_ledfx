from abc import ABC, abstractmethod
from typing import Dict
import requests


class ApiCall(ABC):
    def __init__(self, host: str):
        self._host = host

    @abstractmethod
    def process(self, midi_msg):
        raise NotImplementedError("Please Implement this method")


class OneShot(ApiCall):
    def __init__(self, cfg: Dict):
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
