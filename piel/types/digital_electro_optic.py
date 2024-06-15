import pandas as pd
from typing import Iterable
from .core import NumericalTypes, PielBaseModel
from .digital import BitType


class BitPhaseMap(PielBaseModel):
    """
    This is a mapping of bits to phase.
    """

    bits: Iterable[BitType]
    """
    Iterable of bits.
    """
    phase: Iterable[NumericalTypes]
    """
    Iterable of phases.
    """

    @property
    def dataframe(self):
        return pd.DataFrame(self.dict())
