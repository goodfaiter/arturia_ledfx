import requests
import json
from src.runner import InputProcessor


MIDI_HOST = 'Arturia MiniLab mkII MIDI 1'


def main():
    try:
        api_url = "http://localhost:8888/api/virtuals"
        response = requests.get(api_url)
        print(json.dumps(response.json(), sort_keys=True, indent=2))
    except Exception as e:
        print(e)

    runner = InputProcessor(MIDI_HOST)
    runner.load_from_yaml('config/config.yaml')
    runner.run()


if __name__ == "__main__":
    main()
