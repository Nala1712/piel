from typing import Literal, Iterable

import pandas as pd
from pydantic import ConfigDict
from .core import PielBaseModel

BitsType = str | bytes | int
BitsList = Iterable[BitsType]
HDLSimulator = Literal["icarus", "verilator"]
HDLTopLevelLanguage = Literal["verilog", "vhdl"]

LogicSignalsList = list[str]


class TruthTable(PielBaseModel):
    model_config = ConfigDict(extra="allow")

    input_ports: LogicSignalsList
    output_ports: LogicSignalsList

    @property
    def ports_list(self):
        return self.input_ports + self.output_ports

    @property
    def dataframe(self):
        # Filter out the input_ports and output_ports keys
        data = {k: v for k, v in self.dict().items() if k not in {'input_ports', 'output_ports'}}
        return pd.DataFrame(data)

    @property
    def implementation_dictionary(self):
        # Include only keys specified within input_ports and output_ports
        selected_ports = set(self.input_ports + self.output_ports)
        filtered_dict = {k: v for k, v in self.dict().items() if k in selected_ports}
        return filtered_dict
