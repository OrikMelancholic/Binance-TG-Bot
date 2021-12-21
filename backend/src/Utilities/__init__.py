import json

_max_label = 0


class Logger:
    def __init__(self, label):
        global _max_label

        self.label = label
        if len(label) > _max_label:
            _max_label = len(label)

    def _print(self, status, msg):
        msg = '[%s] %s | %s' % (self.label.ljust(_max_label), status, msg)
        print(msg)

    def log(self, msg):
        self._print('LOG', msg)

    def error(self, msg):
        self._print('ERROR', msg)

    def critical(self, msg):
        self._print('CRITICAL', msg)

    def fancy_json(self, json_data):
        return json.dumps(json_data, sort_keys=True, indent=4)

