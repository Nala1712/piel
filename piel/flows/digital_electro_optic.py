import numpy as np
import pandas as pd
from typing import Iterable, Optional, Callable
from ..types import (
    BitPhaseMap,
    PhaseMapType,
    OpticalStateTransitions,
    TruthTable,
    convert_tuple_to_string,
)


def add_truth_table_bit_phase_data(
    truth_table: TruthTable,
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
        bit_phase_map (BitPhaseMap): The dataframe that maps the phase to the bit.
        rounding_function (Optional[Callable]): The rounding function that is used to round the phase to the nearest
            phase in the phase_bit_dataframe.

    Returns:
        tuple: A tuple of bits that correspond to the phase column of the dataframe.
    """
    bit_list = []
    # Iterate through the dataframe's phase tuples column
    for phase_tuple in truth_table["phase"]: # TODO update on truth table declaration
        # Convert the tuple of phases into bitstrings using convert_phase_array_to_bit_array
        bits = convert_phase_to_bit_iterable(phase_tuple, bit_phase_map, rounding_function)

        # Add the bits to the final list
        bit_list.extend(tuple([bits]))

    return tuple(bit_list)


def convert_optical_transitions_to_truth_table(
    optical_state_transitions: OpticalStateTransitions,
    bit_phase_map = BitPhaseMap
) -> TruthTable:

    ports_list = optical_state_transitions.transmission_data[0].keys()
    output_ports_list = list()
    transitions_dataframe = optical_state_transitions.target_output_dataframe

    phase_bit_array_length = len(transitions_dataframe["phase"][0])
    truth_table_raw = dict()

    # Check if all input and output ports are in the dataframe
    for port_i in ports_list:

        truth_table_raw[port_i] = transitions_dataframe.loc[:, port_i].values

        if port_i == "phase":
            continue

        if not isinstance(transitions_dataframe.loc[0, port_i], tuple):
            print(transitions_dataframe.loc[0, port_i])
            continue

        # TODO implement this for binary mode full
        truth_table_raw[f"{port_i}_str"] = transitions_dataframe.loc[:, port_i].apply(
            convert_tuple_to_string
        )

        truth_table_raw[f"{port_i}_str"] = truth_table_raw[f"{port_i}_str"].apply(
            lambda x: "".join(str(x))
        )



    for phase_iterable_id_i in range(phase_bit_array_length):
        # Initialise lists
        truth_table_raw[f"bit_phase_{phase_iterable_id_i}"] = list()
        output_ports_list += f"bit_phase_{phase_iterable_id_i}"

    for transition_id_i in range(len(transitions_dataframe)):

        bit_phase = convert_phase_to_bit_iterable(
            phase=transitions_dataframe["phase"].iloc[transition_id_i],
            bit_phase_map=bit_phase_map
        )

        for phase_iterable_id_i in range(phase_bit_array_length):
            truth_table_raw[f"bit_phase_{phase_iterable_id_i}"].append(bit_phase[phase_iterable_id_i])

    input_ports = ["input_fock_state_str"]
    output_ports = output_ports_list

    return TruthTable(
        input_ports=input_ports,
        output_ports=output_ports,
        **truth_table_raw,
    )


def convert_phase_to_bit_iterable(
    phase: PhaseMapType,
    bit_phase_map: BitPhaseMap,
    rounding_function: Optional[Callable] = None,
) -> tuple:
    """
    This function converts a phase array or tuple iterable, into the corresponding mapping of their bitstring
    required within a particular bit-phase mapping. A ``phase_array`` iterable is provided, and each phase is mapped
    to a particular bitstring based on the ``phase_bit_dataframe``. A tuple is composed of strings that represent the
    bitstrings of the phases provided.

    Args:
        phase(Iterable): Iterable of phases to map to bitstrings.
        bit_phase_map(BitPhaseMap): Dataframe containing the phase-bits mapping.
        rounding_function(Callable): Rounding function to apply to the target phase.

    Returns:
        bit_array(tuple): Tuple of bitstrings corresponding to the phases.
    """
    # Determine the maximum length of the bitstrings in the dataframe
    # Assumes last bit phase mapping is the largest one
    max_bit_length = len(bit_phase_map.bits[-1])

    bit_array = []

    for phase_i in phase:
        # Apply rounding function if provided
        if rounding_function:
            phase_i = rounding_function(phase_i)

        # Check if phase is in the dataframe
        matched_rows = bit_phase_map.dataframe.loc[bit_phase_map.dataframe["phase"] == phase, "bits"]

        # If exact phase is not found, use the nearest phase bit representation
        if matched_rows.empty:
            bitstring, _ = find_nearest_bit_for_phase(
                phase_i, bit_phase_map, rounding_function
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
