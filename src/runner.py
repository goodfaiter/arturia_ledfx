import mido
from typing import Dict, List
import sys
import yaml
from .api_calls import ApiCall, AdjustBrightness, OneShot, Ripple, SwitchToEffect, SwitchToEffectAndPreset, Wave
from .midi_inputs import MidiInput


def str_to_class(class_name):
    """Turns string class name into python object. Requires all objects to be added above even if not used.

    :param class_name: Name of the class.
    :return: object definition.
    """
    return getattr(sys.modules[__name__], class_name)


class InputProcessor:
    def __init__(self, midi_port: str):
        """Process all midi triggers that map midi key to effects.

        :param midi_port: Name of the midi device to be read from.
        """
        self._midi_port: str = midi_port
        self._midi_triggers: Dict[MidiInput, List[ApiCall]] = {}

    def load_from_yaml(self, file_path: str):
        """Load all API call triggers through `.yaml` file.

        :param file_path: FIle path to the yaml file.
        """
        with open(file_path, 'r') as f:
            output = yaml.safe_load(f)
        for midi_input in output:
            api_calls = []
            for api_call in midi_input['api_calls']:
                api_call_str = list(api_call.keys())[0]
                api_calls.append(str_to_class(api_call_str)(api_call[api_call_str]))
            self._add_midi_trigger(MidiInput(midi_input), api_calls)

    def _add_midi_trigger(self, midi_input: MidiInput, api_calls: List[ApiCall]):
        """Add a midi button and responding api call.

        :param midi_input: Midi input object corresponding to the button pressed.
        :param api_calls: Api calls (list) to call upon the midi button pressed.
        """
        self._midi_triggers[midi_input] = api_calls

    def run(self):
        """Run the main midi to API call processing thread.

        In case of api call errors, we do not exit but continue running.
        """
        with mido.open_input(self._midi_port) as in_port:
            for msg in in_port:
                for midi_input, api_calls in self._midi_triggers.items():
                    if midi_input.match(msg):
                        try:
                            [api_call.process(msg) for api_call in api_calls]
                        except Exception as e:
                            print(e)
                        break
