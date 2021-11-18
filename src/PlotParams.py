from dataclasses import dataclass


@dataclass
class PlotParams:
    current_stage = -1
    market = ""
    currency = ""
    date_interval = ""
    candle_size = ""
