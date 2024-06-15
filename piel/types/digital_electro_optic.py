import pandas as pd
import numpy as np
from typing import Iterable
from .core import NumericalTypes, PielBaseModel
from .digital import BitsType


class BitPhaseMap(PielBaseModel):
    """
    This is a mapping of bits to phase.
    """

    bits: list[BitsType] | tuple[BitsType] | np.ndarray
    """
    Iterable of bits.
    """
    phase: list[NumericalTypes] | tuple[NumericalTypes] | np.ndarray
    """
    Iterable of phases.
    """

    @property
    def dataframe(self):
        return pd.DataFrame(self.dict())
