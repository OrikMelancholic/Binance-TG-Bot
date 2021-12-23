from dataclasses import dataclass


@dataclass
class FavParams:
    current_stage = -1
    current_curr = ""
    currency = ""

    def reset(self):
        self.current_stage = -1
        self.currency = ""
