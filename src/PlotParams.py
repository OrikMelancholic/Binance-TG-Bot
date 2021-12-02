from dataclasses import dataclass


@dataclass
class PlotParams:
    current_stage = -1
    market = ""
    currency = ""
    date_interval = 0
    candle_size = ""
