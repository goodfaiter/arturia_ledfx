from typing import Dict


class MidiInput:
    def __init__(self, cfg: Dict):
        """Definition of the midi input. Fields match Arturia MIDI keyboard.

        :param cfg: Dict containing the midi inputs as per `mido` library.
        """
        self._type = cfg['type']
        self._channel = cfg['channel']
        self._note = cfg['note']
        self._control = cfg['control']

    def match(self, msg) -> bool:
        """Checks if the new midi message given matches the definition of this midi input.

        :param msg: Message from the MIDI keyboard
        :return: True if all msg fields match this midi input.
        """
        if self._type is not None and msg.type != self._type:
            return False
        if self._control is not None and msg.control != self._control:
            return False
        if self._note is not None and msg.note != self._note:
            return False
        if self._channel is not None and msg.channel != self._channel:
            return False
        return True
