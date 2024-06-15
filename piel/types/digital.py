import pandas as pd
from typing import Literal
from .core import PielBaseModel

BitType = str | bytes | int
HDLSimulator = Literal["icarus", "verilator"]
HDLTopLevelLanguage = Literal["verilog", "vhdl"]

LogicSignalsList = list[str]


class TruthTable(PielBaseModel):
    input_ports: LogicSignalsList
    output_ports: LogicSignalsList

    @property
    def ports_list(self):
        return self.input_ports + self.output_ports
