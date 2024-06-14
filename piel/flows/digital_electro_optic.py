import numpy as np
import pandas as pd
from typing import Iterable, Optional, Callable
from ..types import (
    PhaseMapType,
    AmaranthLogicSignals,
    AmaranthTruthTable,
    convert_tuple_to_string,
)


def convert_dataframe_to_bit_tuple(
    dataframe: pd.DataFrame,
    phase_column_name: str,
    phase_bit_dataframe: pd.DataFrame,
    phase_series_name: str = "phase",
    bit_series_name: str = "bit",
    rounding_function: Optional[Callable] = None,
) -> tuple:
    """
    This function converts the phase column of a dataframe into a bit tuple using the phase_bit_dataframe. The
    phase_bit_dataframe is a dataframe that maps the phase to the bit. The phase_series_name is the name of the
    phase series in the phase_bit_dataframe. The bit_series_name is the name of the bit series in the
    phase_bit_dataframe. The phase_column_name is the name of the phase column in the dataframe. The function returns
    a tuple of bits that correspond to the phase column of the dataframe.

    Args:
        dataframe (pd.DataFrame): The dataframe that contains the phase column.
        phase_column_name (str): The name of the phase column in the dataframe.
        phase_bit_dataframe (pd.DataFrame): The dataframe that maps the phase to the bit.
        phase_series_name (str): The name of the phase series in the phase_bit_dataframe.
        bit_series_name (str): The name of the bit series in the phase_bit_dataframe.
        rounding_function (Optional[Callable]): The rounding function that is used to round the phase to the nearest
            phase in the phase_bit_dataframe.

    Returns:
        tuple: A tuple of bits that correspond to the phase column of the dataframe.
    """
    bit_list = []
    # Iterate through the dataframe's phase tuples column
    for phase_tuple in dataframe[phase_column_name]:
        # Convert the tuple of phases into bitstrings using convert_phase_array_to_bit_array
        bits = convert_phase_array_to_bit_array(
            phase_tuple,
            phase_bit_dataframe,
            phase_series_name,
            bit_series_name,
            rounding_function,
        )

        # Add the bits to the final list
        bit_list.extend(tuple([bits]))

    return tuple(bit_list)


def convert_dataframe_to_truth_table_dictionary(
    truth_table_dataframe: pd.DataFrame,
    input_ports: AmaranthLogicSignals,
    output_ports: AmaranthLogicSignals,
) -> AmaranthTruthTable:
    """
    This function converts a dataframe into a truth table dictionary. The truth table dictionary is a dictionary
    where the keys are the port names and the values are the lists of binary strings representing the truth table entries.
    The function ensures that the keys are present in the dataframe and converts the relevant columns to the required format.

    Args:
        truth_table_dataframe (pd.DataFrame): The dataframe that contains the truth table.
        input_ports (List[str]): A list of the input port names in the dataframe.
        output_ports (List[str]): A list of the output port names in the dataframe.

    Returns:
        Dict[str, List[str]]: The truth table dictionary.
    """
    # TODO clean up dirty code.

    # Check if all input and output ports are in the dataframe
    for port_i in input_ports + output_ports:
        if port_i not in truth_table_dataframe.columns:
            raise ValueError(f"Port {port_i} not found in dataframe columns.")

        truth_table_dataframe[port_i] = truth_table_dataframe.loc[:, port_i].apply(
            convert_tuple_to_string
        )

        truth_table_dataframe[port_i] = truth_table_dataframe[port_i].apply(
            lambda x: "".join(x)
        )

    # Construct the dictionary with input and output ports
    truth_table_dict = {
        port_i: truth_table_dataframe[port_i].to_list()
        for port_i in input_ports + output_ports
    }

    return truth_table_dict


def convert_phase_array_to_bit_array(
    phase_array: Iterable,
    phase_bit_dataframe: pd.DataFrame,
    phase_series_name: str = "phase",
    bit_series_name: str = "bit",
    rounding_function: Optional[Callable] = None,
) -> tuple:
    """
    This function converts a phase array or tuple iterable, into the corresponding mapping of their bitstring
    required within a particular bit-phase mapping. A ``phase_array`` iterable is provided, and each phase is mapped
    to a particular bitstring based on the ``phase_bit_dataframe``. A tuple is composed of strings that represent the
    bitstrings of the phases provided.

    Args:
        phase_array(Iterable): Iterable of phases to map to bitstrings.
        phase_bit_dataframe(pd.DataFrame): Dataframe containing the phase-bit mapping.
        phase_series_name(str): Name of the phase series in the dataframe.
        bit_series_name(str): Name of the bit series in the dataframe.
        rounding_function(Callable): Rounding function to apply to the target phase.

    Returns:
        bit_array(tuple): Tuple of bitstrings corresponding to the phases.
    """
    # Determine the maximum length of the bitstrings in the dataframe
    max_bit_length = phase_bit_dataframe[bit_series_name].apply(len).max()

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

        # Pad the bitstring to the maximum length
        full_length_bitstring = bitstring.zfill(max_bit_length)

        bit_array.append(full_length_bitstring)

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
