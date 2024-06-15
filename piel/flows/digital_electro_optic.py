import numpy as np
import pandas as pd
from typing import Iterable, Optional, Callable
from ..types import (
    BitPhaseMap,
    TruthTable,
    convert_tuple_to_string,
)


def convert_dataframe_to_bit_tuple(
    truth_table: TruthTable,
    phase_column_name: str,
    bit_phase_map: BitPhaseMap,
    rounding_function: Optional[Callable] = None,
) -> tuple:
    """
    This function converts the phase column of a dataframe into a bit tuple using the phase_bit_dataframe. The
    phase_bit_dataframe is a dataframe that maps the phase to the bit. The phase_series_name is the name of the
    phase series in the phase_bit_dataframe. The bit_series_name is the name of the bit series in the
    phase_bit_dataframe. The phase_column_name is the name of the phase column in the dataframe. The function returns
    a tuple of bits that correspond to the phase column of the dataframe.

    Args:
        truth_table (pd.DataFrame): The dataframe that contains the phase column.
        phase_column_name (str): The name of the phase column in the dataframe.
        bit_phase_map (BitPhaseMap): The dataframe that maps the phase to the bit.
        rounding_function (Optional[Callable]): The rounding function that is used to round the phase to the nearest
            phase in the phase_bit_dataframe.

    Returns:
        tuple: A tuple of bits that correspond to the phase column of the dataframe.
    """
    # TODO interim pydantic-dataframe migration
    bit_phase_map = bit_phase_map.dataframe

    bit_list = []
    # Iterate through the dataframe's phase tuples column
    for phase_tuple in truth_table[phase_column_name]:
        # Convert the tuple of phases into bitstrings using convert_phase_array_to_bit_array
        bits = convert_phase_array_to_bit_array(
            phase_tuple, bit_phase_map, rounding_function
        )

        # Add the bits to the final list
        bit_list.extend(tuple([bits]))

    return tuple(bit_list)


# def convert_dataframe_to_truth_table_dictionary(
#     truth_table: TruthTable,
# ) -> TruthTable:
#     """
#     This function converts a dataframe into a truth table dictionary. The truth table dictionary is a dictionary
#     where the keys are the port names and the values are the lists of binary strings representing the truth table entries.
#     The function ensures that the keys are present in the dataframe and converts the relevant columns to the required format.
#
#     Args:
#         truth_table (pd.DataFrame): The dataframe that contains the truth table.
#         input_ports (List[str]): A list of the input port names in the dataframe.
#         output_ports (List[str]): A list of the output port names in the dataframe.
#
#     Returns:
#         Dict[str, List[str]]: The truth table dictionary.
#     """
#     # TODO clean up dirty code.
#     ports_list = TruthTable.ports_list
#     truth_table = TruthTable.dataframe
#
#     # Check if all input and output ports are in the dataframe
#     for port_i in ports_list:
#         if port_i not in truth_table.columns:
#             raise ValueError(f"Port {port_i} not found in dataframe columns.")
#
#         truth_table[port_i] = truth_table.loc[:, port_i].apply(
#             convert_tuple_to_string
#         )
#
#         truth_table[port_i] = truth_table[port_i].apply(
#             lambda x: "".join(x)
#         )
#
#     # Construct the dictionary with input and output ports
#     truth_table_dict = {
#         port_i: truth_table[port_i].to_list()
#         for port_i in ports_list
#     }
#
#     return truth_table_dict


def convert_phase_array_to_bit_array(
    phase_array: Iterable,
    bit_phase_map: BitPhaseMap,
    rounding_function: Optional[Callable] = None,
) -> tuple:
    """
    This function converts a phase array or tuple iterable, into the corresponding mapping of their bitstring
    required within a particular bit-phase mapping. A ``phase_array`` iterable is provided, and each phase is mapped
    to a particular bitstring based on the ``phase_bit_dataframe``. A tuple is composed of strings that represent the
    bitstrings of the phases provided.

    Args:
        phase_array(Iterable): Iterable of phases to map to bitstrings.
        bit_phase_map(BitPhaseMap): Dataframe containing the phase-bits mapping.
        rounding_function(Callable): Rounding function to apply to the target phase.

    Returns:
        bit_array(tuple): Tuple of bitstrings corresponding to the phases.
    """
    # TODO interim pydantic-dataframe migration
    bit_phase_map = bit_phase_map.dataframe

    # Determine the maximum length of the bitstrings in the dataframe
    max_bit_length = bit_phase_map["bits"].apply(len).max()

    bit_array = []

    for phase in phase_array:
        # Apply rounding function if provided
        if rounding_function:
            phase = rounding_function(phase)

        # Check if phase is in the dataframe
        matched_rows = bit_phase_map.loc[bit_phase_map["phase"] == phase, "bits"]

        # If exact phase is not found, use the nearest phase bit representation
        if matched_rows.empty:
            bitstring, _ = find_nearest_bit_for_phase(
                phase, bit_phase_map, rounding_function
            )
        else:
            bitstring = matched_rows.iloc[0]

        # Pad the bitstring to the maximum length
        full_length_bitstring = bitstring.zfill(max_bit_length)

        bit_array.append(full_length_bitstring)

    return tuple(bit_array)


def find_nearest_bit_for_phase(
    target_phase: float,
    bit_phase_map: BitPhaseMap,
    rounding_function: Optional[Callable] = None,
) -> tuple:
    """
    This is a mapping function between a provided target phase that might be more analogous, with the closest
    bit-value in a `bit-phase` ideal relationship. The error between the target phase and the applied phase is
    limited to the discretisation error of the phase mapping.

    Args:
        target_phase(float): Target phase to map to.
        bit_phase_map(pd.DataFrame): Dataframe containing the phase-bits mapping.
        rounding_function(Callable): Rounding function to apply to the target phase.

    Returns:
        bitstring(str): Bitstring corresponding to the nearest phase.
    """
    # TODO interim pydantic-dataframe migration
    bit_phase_map = bit_phase_map.dataframe

    # Apply rounding function if provided
    if rounding_function:
        target_phase = rounding_function(target_phase)

    # Find the nearest phase from the dataframe
    phases = bit_phase_map["phase"].values
    nearest_phase = phases[
        np.argmin(np.abs(phases - target_phase))
    ]  # TODO implement rounding function here.

    # Get the corresponding bitstring for the nearest phase
    bitstring = bit_phase_map.loc[bit_phase_map["phase"] == nearest_phase, "bits"].iloc[
        0
    ]

    return bitstring, nearest_phase


def return_phase_array_from_data_series(
    data_series: pd.Series,
    phase_map: BitPhaseMap,
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
