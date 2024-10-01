import argparse
import json
import requests
from arturia_ledfx.runner import InputProcessor


MIDI_HOST = 'Arturia MiniLab mkII MIDI 1'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", type=str)
    args = parser.parse_args()

    try:
        api_url = "http://localhost:8888/api/virtuals"
        response = requests.get(api_url)
        print(json.dumps(response.json(), sort_keys=True, indent=2))
    except Exception as e:
        print(e)

    runner = InputProcessor(MIDI_HOST)
    runner.load_from_yaml(args.config)
    runner.run()
