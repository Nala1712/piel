import pandas as pd

from .core import NumericalTypes, PielBaseModel


class PhaseBitDataFrame(PielBaseModel):
    bits: list[str]
    phase: list[NumericalTypes]

    @property
    def dataframe(self):
        return pd.DataFrame(self.dict)


PhaseMapType = PhaseBitDataFrame
