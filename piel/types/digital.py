from typing import Literal, Iterable
from .core import PielBaseModel

BitsType = str | bytes | int
BitsList = Iterable[BitsType]
HDLSimulator = Literal["icarus", "verilator"]
HDLTopLevelLanguage = Literal["verilog", "vhdl"]

LogicSignalsList = list[str]


class TruthTable(PielBaseModel):
    input_ports: LogicSignalsList
    output_ports: LogicSignalsList

    @property
    def ports_list(self):
        return self.input_ports + self.output_ports
