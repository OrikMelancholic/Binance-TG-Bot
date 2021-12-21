from dataclasses import dataclass


@dataclass
class PlotParams:
    current_stage = -1
    market = ""
    currency = ""
    date_interval = 0
    candle_size = ""

    def reset(self):
        self.current_stage = -1
        self.market = ""
        self.currency = ""
        self.date_interval = 0
        self.candle_size = ""