"""
TODO implement this function.
In this function we implement different methods of mapping electronic signals to phase.

One particular implementation of phase mapping would be:

.. list-table:: Example Basic Phase Mapping
   :header-rows: 1

   * - Bit
     - Phase
   * - b0
     - :math:`\\phi_0 \\to 0`
   * - b1
     - :math:`\\phi_1 \\to \\pi`

We can define the two corresponding angles that this would be.

A more complex implementation of phase mapping can be similar to a DAC mapping: a bitstring within a converter
bit-size can map directly to a particular phase space within a particular mapping."""
import numpy as np
import pandas as pd
from typing import Literal

from ..electronic.digital import bits_array_from_bits_amount
from ....types.digital_electro_optic import BitPhaseMap
from ....types.digital import BitType


def linear_bit_phase_map(
    bits_amount: int,
    final_phase_rad: float,
    initial_phase_rad: float = 0,
    quantization_error: float = 0.000001,
    bit_format: BitType = int,
) -> BitPhaseMap:
    """
    Returns a linear direct mapping of bits to phase.

    Args:
        bits_amount(int): Amount of bits to generate.
        final_phase_rad(float): Final phase to map to.
        initial_phase_rad(float): Initial phase to map to.
        quantization_error(float): Error in the phase mapping.
        bit_format(Literal["int", "str"]): Format of the bits.


    Returns:
        bit_phase_mapping(dict): Mapping of bits to phase.
    """
    bits_array = bits_array_from_bits_amount(bits_amount)
    phase_division_amount = len(bits_array) - 1
    phase_division_step = (
                              final_phase_rad - initial_phase_rad
                          ) / phase_division_amount - quantization_error
    linear_phase_array = np.arange(
        initial_phase_rad, final_phase_rad, phase_division_step
    )

    if bit_format == int:
        pass
    elif bit_format == str:
        bits_array = bits_array_from_bits_amount(bits_amount, bit_format=bit_format)

    bit_phase_mapping_raw = {
        "bits": bits_array,
        "phase": linear_phase_array,
    }
    bit_phase_mapping = BitPhaseMap(**bit_phase_mapping_raw)
    return bit_phase_mapping
