import numpy as np
import pandas as pd
from typing import Iterable, Optional, Callable
from ..types import PhaseMapType


def convert_phase_array_to_bit_array(
    phase_array: Iterable,
    phase_bit_dataframe: pd.DataFrame,
    phase_series_name: str = "phase",
    bit_series_name: str = "bit",
    rounding_function: Optional[Callable] = None,
) -> tuple:
    """
    This function converts a phase array or tuple iterable, into the corresponding mapping of their bitstring required within a particular bit-phase mapping. A ``phase_array`` iterable is provided, and each phase is mapped to a particular bitstring based on the ``phase_bit_dataframe``. A tuple is composed of strings that represent the bitstrings of the phases provided.

    Args:
        phase_array(Iterable): Iterable of phases to map to bitstrings.
        phase_bit_dataframe(pd.DataFrame): Dataframe containing the phase-bit mapping.
        phase_series_name(str): Name of the phase series in the dataframe.
        bit_series_name(str): Name of the bit series in the dataframe.
        rounding_function(Callable): Rounding function to apply to the target phase.

    Returns:
        bit_array(tuple): Tuple of bitstrings corresponding to the phases.
    """
    bit_array = []

    for phase in phase_array:
        # Apply rounding function if provided
        if rounding_function:
            phase = rounding_function(phase)

        # Check if phase is in the dataframe
        matched_rows = phase_bit_dataframe.loc[
            phase_bit_dataframe[phase_series_name] == phase, bit_series_name
        ]

        # If exact phase is not found, use the nearest phase bit representation
        if matched_rows.empty:
            bitstring, _ = find_nearest_bit_for_phase(
                phase,
                phase_bit_dataframe,
                phase_series_name,
                bit_series_name,
                rounding_function,
            )
        else:
            bitstring = matched_rows.iloc[0]

        bit_array.append(bitstring)

    return tuple(bit_array)


def find_nearest_bit_for_phase(
    target_phase: float,
    phase_bit_dataframe: pd.DataFrame,
    phase_series_name: str = "phase",
    bit_series_name: str = "bit",
    rounding_function: Optional[Callable] = None,
) -> tuple:
    """
    This is a mapping function between a provided target phase that might be more analogous, with the closest
    bit-value in a `bit-phase` ideal relationship. The error between the target phase and the applied phase is
    limited to the discretisation error of the phase mapping.

    Args:
        target_phase(float): Target phase to map to.
        phase_bit_dataframe(pd.DataFrame): Dataframe containing the phase-bit mapping.
        phase_series_name(str): Name of the phase series in the dataframe.
        bit_series_name(str): Name of the bit series in the dataframe.
        rounding_function(Callable): Rounding function to apply to the target phase.

    Returns:
        bitstring(str): Bitstring corresponding to the nearest phase.
    """
    # Apply rounding function if provided
    if rounding_function:
        target_phase = rounding_function(target_phase)

    # Find the nearest phase from the dataframe
    phases = phase_bit_dataframe[phase_series_name].values
    nearest_phase = phases[
        np.argmin(np.abs(phases - target_phase))
    ]  # TODO implement rounding function here.

    # Get the corresponding bitstring for the nearest phase
    bitstring = phase_bit_dataframe.loc[
        phase_bit_dataframe[phase_series_name] == nearest_phase, bit_series_name
    ].iloc[0]

    return bitstring, nearest_phase


def return_phase_array_from_data_series(
    data_series: pd.Series,
    phase_map: PhaseMapType,
) -> list:
    """
    Returns a list of phases from a given data series and phase map.
    # TODO optimise lookup table speed

    Args:
        data_series(pd.Series): Data series to map.
        phase_map(pd.DataFrame | pd.Series): Phase map to use.

    Returns:
        phase_array(list): List of phases.
    """
    phase_array = []
    for code_i in data_series.values:
        phase = phase_map[phase_map.bits == str(code_i)].phase.values[0]
        phase_array.append(phase)
    return phase_array
