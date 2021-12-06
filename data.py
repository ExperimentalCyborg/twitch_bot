import os
import sys
import json


class Data:

    def __init__(self, channel_default_settings):
        self.data_path = os.path.join(os.getcwd(), 'data')
        if not os.path.isdir(self.data_path):
            os.mkdir(self.data_path)
        self.data = {}
        self.datafile_postfix = '.settings.json'
        self.default_channel_data = {
            'settings': channel_default_settings,
            'commands': {}
        }

        self._load_all()

    def command_add(self, channel: str, key: str, value: object):
        self.data[channel]['commands'][key] = value
        self._update_channel_data(channel)

    def command_remove(self, channel: str, key: str):
        del self.data[channel]['commands'][key]
        self._update_channel_data(channel)

    def command_list(self, channel: str):
        return list(self.data[channel]['commands'])

    def command_get(self, channel: str, key: str):
        return self.data[channel]['commands'].get(key, None)

    def channel_add(self, channel: str):
        self.data[channel] = self._load_or_make_channel_data(channel)

    def channel_remove(self, channel: str):
        del self.data[channel]
        file_path = os.path.join(self.data_path, channel)
        try:
            os.remove(file_path)
        except OSError:
            print(f'Failed to remove file "{file_path}": {e}', file=sys.stderr)

    def channel_setting(self, channel: str, key: str, value: str = None):
        stored_value = self.data[channel]['settings'].get(key, None)

        if value is not None and stored_value is not value:
            self.data[channel]['settings'][key] = value
            self._update_channel_data(channel)
            return value

        return stored_value

    def channel_list(self):
        files = os.listdir(self.data_path)
        return [fname[:-len(self.datafile_postfix)] for fname in files if fname.endswith(self.datafile_postfix)]

    def _load_or_make_channel_data(self, channel: str):
        file_path = os.path.join(self.data_path, f'{channel}{self.datafile_postfix}')
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf8') as f:
                    return json.loads(f.read())
            except OSError as e:
                print(f'Failed to read file "{file_path}": {e}', file=sys.stderr)
            except json.JSONDecodeError as e:
                print(f'Failed to decode file "{file_path}": {e}', file=sys.stderr)
        else:
            try:
                with open(file_path, 'w', encoding='utf8') as f:
                    f.write(json.dumps(self.default_channel_data))
            except OSError as e:
                print(f'Failed to write file "{file_path}": {e}', file=sys.stderr)
            return self.default_channel_data

    def _update_channel_data(self, channel: str):
        file_path = os.path.join(self.data_path, f'{channel}{self.datafile_postfix}')
        try:
            with open(file_path, 'w', encoding='utf8') as f:
                f.write(json.dumps(self.data[channel]))
        except OSError as e:
            print(f'Failed to write file "{file_path}": {e}', file=sys.stderr)

    def _load_all(self):
        for channel in self.channel_list():
            self.data[channel] = self._load_or_make_channel_data(channel)
