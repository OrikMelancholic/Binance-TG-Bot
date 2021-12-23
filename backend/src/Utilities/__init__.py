import json
import logging

_max_label = 0


class Logger:
    def __init__(self, label):
        global _max_label

        self.label = label
        if len(label) > _max_label:
            _max_label = len(label)

    def _print(self, msg):
        msg = '[%s] | %s' % (self.label.ljust(_max_label), msg)
        return msg

    def log(self, msg):
        logging.info(self._print(msg))

    def warning(self, msg):
        logging.warning(self._print(msg))

    def debug(self, msg):
        logging.debug(self._print(msg))

    def error(self, msg):
        logging.error(self._print(msg))

    def critical(self, msg):
        logging.critical(self._print(msg))

    def fancy_json(self, json_data):
        return json.dumps(json_data, sort_keys=True, indent=4)

