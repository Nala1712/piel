import gdsfactory as gf
import jax.numpy as jnp
from itertools import product
from typing import Optional, Callable
from ..tools.sax.netlist import (
    address_value_dictionary_to_function_parameter_dictionary,
    get_matched_model_recursive_netlist_instances,
)
from ..tools.sax.utils import sax_to_s_parameters_standard_matrix
from ..integration.thewalrus_qutip import fock_transition_probability_amplitude
from .electro_optic import generate_s_parameter_circuit_from_photonic_circuit


def compose_phase_address_state(
    switch_instance_map: dict,
    switch_phase_permutation_map: dict,
) -> dict:
    """
    This function composes the phase shifter address state for each circuit. This means that we have a dictionary
    that maps the instance address to the phase shifter state. This is then used to compose the function parameter
    state.

    Args:
        circuits (dict): The dictionary of the circuits.
        switch_instance_map (dict): The dictionary of the switch instances.
        switch_phase_permutation_map (dict): The dictionary of the switch phase permutations.

    Returns:
        phase_shifter_address_state (dict): The dictionary of the phase shifter address state.
    """
    phase_shifter_address_state = dict()
    for i in range(len(switch_phase_permutation_map)):
        phase_shifter_address_state[i] = dict()
        phase_shifter_address_state[i].update(
            {
                instance_address_i: switch_phase_i
                for instance_address_i, switch_phase_i in zip(
                    switch_instance_map,
                    switch_phase_permutation_map[i],
                    strict=False,
                )
            }
        )
    return phase_shifter_address_state


def compose_switch_function_parameter_state(
    switch_phase_address_state: dict,
) -> dict:
    """
    This function composes the combinations of the phase shifter inputs into a form that can be inputted into sax for
    each particular address.

    Args:
        switch_phase_address_state (dict): The dictionary of the switch phase address state.

    Returns:
        phase_shifter_function_parameter_state (dict): The dictionary of the phase shifter function parameter state.
    """
    phase_shifter_function_parameter_state = dict()
    for id_i, phase_address_map in switch_phase_address_state.items():
        phase_shifter_function_parameter_state[id_i] = address_value_dictionary_to_function_parameter_dictionary(
            address_value_dictionary=phase_address_map,
            parameter_key="active_phase_rad",
        )
    return phase_shifter_function_parameter_state


def calculate_switch_unitaries(
    circuit: Callable,
    switch_function_parameter_state: dict,
) -> dict:
    implemented_unitary_dictionary = dict()
    for id_i, function_parameter_state_i in switch_function_parameter_state.items():
        sax_s_parameters_i = circuit(**function_parameter_state_i)
        implemented_unitary_dictionary[id_i] = sax_to_s_parameters_standard_matrix(sax_s_parameters_i)
    return implemented_unitary_dictionary


def calculate_all_transition_probability_amplitudes(
    unitary_matrix: jnp.ndarray,
    input_fock_states: list,
    output_fock_states: list,
) -> dict:
    """
    This tells us the transition probabilities between our photon states for a particular implemented unitary.
    """
    i = 0
    circuit_transition_probability_data_i = dict()
    for input_fock_state in input_fock_states:
        for output_fock_state in output_fock_states:
            fock_transition_probability_amplitude_i = (
                fock_transition_probability_amplitude(
                    initial_fock_state=input_fock_state,
                    final_fock_state=output_fock_state,
                    unitary_matrix=unitary_matrix,
                )
            )
            data = {
                "input_fock_state": input_fock_state,
                "output_fock_state": output_fock_state,
                "fock_transition_probability_amplitude": fock_transition_probability_amplitude_i,
            }
            circuit_transition_probability_data_i[i] = data
            i += 1
    return circuit_transition_probability_data_i


def calculate_classical_transition_probability_amplitudes(
    unitary_matrix: jnp.ndarray,
    input_fock_states: list,
    target_mode_index: Optional[int] = None,
    determine_ideal_mode_function: Optional[Callable] = None,
) -> dict:
    """
    This tells us the classical transition probabilities between our photon states for a particular implemented
    s-parameter transformation.

    Note that if no target_mode_index is provided, then the determine_ideal_mode_function will analyse
    the provided data and return the target mode and append the relevant probability data to the data dictionary. It will
    raise an error if no method is implemented.
    """
    circuit_transition_probability_data = {}

    for i, input_fock_state in enumerate(input_fock_states):
        mode_transformation = jnp.dot(unitary_matrix, input_fock_state)
        classical_transition_mode_probability = jnp.abs(
            mode_transformation
        )  # Assuming probabilities are the squares of the amplitudes

        if target_mode_index is not None:
            if (
                isinstance(
                    classical_transition_mode_probability[target_mode_index],
                    jnp.ndarray,
                )
                and classical_transition_mode_probability[target_mode_index].ndim == 1
            ):
                classical_transition_target_mode_probability = (
                    classical_transition_mode_probability[target_mode_index].item()
                )
            else:
                classical_transition_target_mode_probability = float(
                    classical_transition_mode_probability[target_mode_index]
                )
        elif determine_ideal_mode_function is not None:
            target_mode_index = determine_ideal_mode_function(mode_transformation)
            classical_transition_target_mode_probability = (
                classical_transition_mode_probability[target_mode_index]
            )
        else:
            raise ValueError(
                "No target mode index provided and no method to determine it."
            )

        data = {
            "input_fock_state": input_fock_state,
            "mode_transformation": mode_transformation,
            "classical_transition_mode_probability": classical_transition_mode_probability,
            "classical_transition_target_mode_probability": classical_transition_target_mode_probability,
        }

        circuit_transition_probability_data[i] = data

    return circuit_transition_probability_data


def construct_unitary_transition_probability_performance(
    unitary_phase_implementations_dictionary: dict,
    input_fock_states: list,
    output_fock_states: list,
):
    """
    This function determines the Fock state probability performance for a given implemented unitary. This means we iterate over each circuit, then each implemented unitary, and we determine the probability transformation accordingly.
    """
    implemented_unitary_probability_dictionary = dict()
    for id_i, circuit_unitaries_i in unitary_phase_implementations_dictionary.items():
        implemented_unitary_probability_dictionary[id_i] = dict()
        for id_i_i, implemented_unitaries_i in circuit_unitaries_i.items():
            implemented_unitary_probability_dictionary[id_i][
                id_i_i
            ] = calculate_all_transition_probability_amplitudes(
                unitary_matrix=implemented_unitaries_i[0],
                input_fock_states=input_fock_states,
                output_fock_states=output_fock_states,
            )
    return implemented_unitary_probability_dictionary


def compose_network_matrix_from_models(
    circuit: gf.Component,
    models: dict,
    switch_states: list,
    top_level_instance_prefix: str = "component_lattice_generic",
    target_component_prefix: str = "mzi",
):
    """
    This function composes the network matrix from the models dictionary and the switch states. It does this by first composing the switch functions, then composing the switch matrix, then composing the network matrix. It returns the network matrix and the switch matrix.

    Args:
        circuit (gf.Component): The circuit.
        models (dict): The models dictionary.
        switch_states (list): The list of switch states.
        top_level_instance_prefix (str): The top level instance prefix.
        target_component_prefix (str): The target component prefix.

    Returns:
        network_matrix (np.ndarray): The network matrix.
    """
    # Compose the netlists as functions
    (
        switch_fabric_circuit,
        switch_fabric_circuit_info_i,
    ) = generate_s_parameter_circuit_from_photonic_circuit(
        circuit=circuit,
        models=models,
    )

    netlist = circuit.get_netlist_recursive(allow_multiple=True)
    # TODO finish cleaning up
    # Now we will iterate through each netlist, and determine all the switch instances
    # switch_fabric_switch_instance_dictionary = dict()
    # for (
    #     id_i,
    #     netlist,
    # ) in network_netlist_dictionary.items():

    switch_instance_list_i = get_matched_model_recursive_netlist_instances(
        recursive_netlist=netlist,
        top_level_instance_prefix=top_level_instance_prefix,
        target_component_prefix=target_component_prefix,
        models=models,
    )
    # switch_fabric_switch_instance_dictionary[id_i] = switch_instance_list_i

    # Apply phases and determine the output
    switch_fabric_switch_phase_configurations = dict()
    # for (
    #     id_i,
    #     switch_instance_list_i,
    # ) in switch_fabric_switch_instance_dictionary.items():
    print("switch_instance_list_i")
    print(switch_instance_list_i)
    switch_amount = len(switch_instance_list_i)
    switch_instance_valid_phase_configurations_i = []
    for phase_configuration_i in product(switch_states, repeat=switch_amount):
        switch_instance_valid_phase_configurations_i.append(phase_configuration_i)
    # switch_fabric_switch_phase_configurations[
    #     id_i
    # ] = switch_instance_valid_phase_configurations_i

    switch_fabric_switch_phase_address_state = compose_phase_address_state(
        switch_instance_map=switch_instance_list_i,
        switch_phase_permutation_map=switch_instance_valid_phase_configurations_i,
    )
    print("switch_fabric_switch_phase_address_state")
    print(switch_fabric_switch_phase_address_state)

    switch_fabric_switch_function_parameter_state = compose_switch_function_parameter_state(
            switch_phase_address_state=switch_fabric_switch_phase_address_state
    )
    print("switch_fabric_switch_function_parameter_state")
    print(switch_fabric_switch_function_parameter_state)
    switch_fabric_switch_unitaries = calculate_switch_unitaries(
        circuit=switch_fabric_circuit,
        switch_function_parameter_state=switch_fabric_switch_function_parameter_state,
    )
    return (
        switch_fabric_switch_unitaries,
        switch_fabric_switch_function_parameter_state,
        switch_fabric_switch_phase_address_state,
        switch_fabric_switch_phase_address_state,
        switch_fabric_switch_phase_configurations,
        switch_instance_list_i,
        switch_fabric_circuit,
        switch_fabric_circuit_info_i,
    )
