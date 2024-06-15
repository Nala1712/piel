import pandas as pd
from typing import Literal

BitType = str | bytes | int
HDLSimulator = Literal["icarus", "verilator"]
HDLTopLevelLanguage = Literal["verilog", "vhdl"]

TruthTableDataFrame = pd.DataFrame
TruthTableDictionary = dict[str, list[str] | tuple[str]]
LogicSignalsList = list[str]
