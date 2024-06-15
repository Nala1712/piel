import pandas as pd

from .core import NumericalTypes, PielBaseModel
from .digital import BitType


class BitPhaseMap(PielBaseModel):

    bits: list[BitType]
    phase: list[NumericalTypes]

    @property
    def dataframe(self):
        return pd.DataFrame(self.dict())
