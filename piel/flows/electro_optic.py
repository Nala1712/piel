import jax.numpy as jnp  # TODO add typing
import gdsfactory as gf
import sax
from typing import Callable
from ..types import (
    absolute_to_threshold,
    convert_array_type,
    ArrayTypes,
    NumericalTypes,
    FockStatePhaseTransitionType,
    TupleIntType,
)
from ..tools.qutip import fock_states_only_individual_modes
from ..tools.sax import sax_to_s_parameters_standard_matrix
from ..models.frequency.defaults import get_default_models


def extract_phase(
    phase_transition_list: list[FockStatePhaseTransitionType], transition_type="cross"
):
    """
    Extracts the phase corresponding to the specified transition type.

    Parameters:
        phase_transition_list (list of dict): Data structure containing phase transition information.
        transition_type (str): Type of transition to extract phase for ('cross' or 'bar').

    Returns:
        float: Phase corresponding to the specified transition type.
    """
    transition_mapping = {"cross": ((1, 0), (0, 1)), "bar": ((1, 0), (1, 0))}

    if transition_type not in transition_mapping:
        raise ValueError("Invalid transition type. Use 'cross' or 'bar'.")

    input_state, output_state = transition_mapping[transition_type]

    for entry in phase_transition_list:
        if (
            entry["input_fock_state"] == input_state
            and entry["output_fock_state"] == output_state
        ):
            return entry["phase"][0]

    raise ValueError(f"Phase for the {transition_type} transition not found.")


def format_electro_optic_fock_transition(
    switch_state_array: ArrayTypes,
    input_fock_state_array: ArrayTypes,
    raw_output_state: ArrayTypes,
) -> FockStatePhaseTransitionType:
    """
    Formats the electro-optic state into a standard FockStatePhaseTransitionType format. This is useful for the
    electro-optic model to ensure that the output state is in the correct format. The output state is a dictionary
    that contains the phase, input fock state, and output fock state. The idea is that this will allow us to
    standardise and compare the output states of the electro-optic model across multiple formats.

    Args:
        switch_state_array(array_types): Array of switch states.
        input_fock_state_array(array_types): Array of valid input fock states.
        raw_output_state(array_types): Array of raw output state.

    Returns:
        electro_optic_state(FockStatePhaseTransitionType): Electro-optic state.
    """
    electro_optic_state = {
        "phase": convert_array_type(switch_state_array, "tuple"),
        "input_fock_state": convert_array_type(input_fock_state_array, TupleIntType),
        "output_fock_state": absolute_to_threshold(
            raw_output_state, output_array_type=TupleIntType
        ),
    }
    # assert type(electro_optic_state) == FockStatePhaseTransitionType # TODO fix this
    return electro_optic_state


def generate_s_parameter_circuit_from_photonic_circuit(
    circuit: gf.Component,
    models: sax.ModelFactory = None,
) -> tuple[any, any]:
    """
    Generates the S-parameters and related information for a given circuit using SAX and custom models.

    Args:
        circuit (gf.Component): The circuit for which the S-parameters are to be generated.
        models (sax.ModelFactory, optional): The models to be used for the S-parameter generation. Defaults to None.

    Returns:
        tuple[any, any]: The S-parameters circuit and related information.
    """
    # Step 1: Retrieve default models if not provided
    if models is None:
        models = get_default_models()

    # Step 2: Generate the netlist recursively
    netlist = circuit.get_netlist_recursive(allow_multiple=True)

    try:
        # Step 7: Compute the S-parameters using the custom library and netlist
        s_parameters, s_parameters_info = sax.circuit(
            netlist=netlist,
            models=models,
            ignore_missing_ports=True,
        )
    except Exception as e:
        """
        Custom exception mapping.
        """
        # Step 3: Identify the top-level circuit name
        top_level_name = circuit.get_netlist()["name"]

        # Step 4: Get required models for the top-level circuit
        required_models = sax.get_required_circuit_models(
            netlist[top_level_name], models=models
        )

        specific_model_key = [
            model
            for model in required_models
            if model.startswith(
                "mzi"
            )  # should technically be the top level recursive component
        ][0]

        specific_model_required = sax.get_required_circuit_models(
            netlist[specific_model_key],
            models=models,
        )
        print("Error in generating S-parameters. Check the following:")
        print("Required models for the top-level circuit:")
        print(required_models)
        print("Required models for the specific model:")
        print(specific_model_key)
        print("Required models for the specific model:")
        print(specific_model_required)

        raise e

    return s_parameters, s_parameters_info


def get_state_phase_transitions(
    switch_function: Callable,
    switch_states: list[NumericalTypes] | None = None,
    input_fock_states: list[ArrayTypes] | None = None,
    mode_amount: int | None = None,
    **kwargs,
) -> list[ArrayTypes]:
    """
    The goal of this function is to extract the corresponding phase required to implement a state transition.

    Let's consider a simple MZI 2x2 logic with two transmission states. We want to verify that the electronic function
    switch, effectively switches the optical output between the cross and bar states of the optical transmission function.

    For the corresponding switch model:

    Let's assume a switch model unitary. For a given 2x2 input optical switch "X". In bar state, in dual rail, transforms an optical input:
    ```
    .. raw::

        [[1] ----> [[1]
        [0]]        [0]]

    In cross state, in dual rail, transforms an optical input:

    .. raw::

        [[1] ----> [[0]
        [0]]        [1]]

    However, sometimes it is easier to describe a photonic logic transformation based on these states, rather than inherently
    the numerical phase that is applied. This may be the case, for example, in asymmetric Mach-Zehnder modulators models, etc.

    As such, this function will help us extract the corresponding phase for a particular switch transition.
    """
    # We compose the switch_states we want to apply
    if switch_states is None:
        switch_states = [0, jnp.pi]

    # We compose the fock states we want to apply
    if input_fock_states is None:
        input_fock_states = fock_states_only_individual_modes(
            mode_amount=mode_amount,
            maximum_photon_amount=1,
            output_type="jax",
        )

    circuits = list()
    output_states = list()
    for switch_state_i in switch_states:
        # Get the transmission matrix for the switch state
        circuit_i = sax_to_s_parameters_standard_matrix(
            # TODO maybe generalise the switch address state mapping into a corresponding function
            switch_function(sxt={"active_phase_rad": switch_state_i}),
            **kwargs,
        )

        # See if the switch state is correctly applied to the input fock states
        for input_fock_state_i in input_fock_states:
            raw_output_state_i = jnp.dot(circuit_i[0], input_fock_state_i)
            output_state_i = format_electro_optic_fock_transition(
                switch_state_array=(switch_state_i,),
                input_fock_state_array=input_fock_state_i,
                raw_output_state=raw_output_state_i,
            )
            output_states.append(output_state_i)
            # Now we need to find a way to verify that the model is correct by comparing to our expectation output.
            # We can do this by comparing the output state to the target fock state.
    return output_states


def get_state_to_phase_map(
    switch_function: Callable,
    switch_states: list[NumericalTypes] | None = None,
    input_fock_states: list[ArrayTypes] | None = None,
    target_transition_list: list[dict] | None = None,
    mode_amount: int | None = None,
    **kwargs,
) -> tuple[ArrayTypes]:
    """
    The goal of this function is to extract the corresponding phase required to implement a state transition.

    Let's consider a simple MZI 2x2 logic with two transmission states. We want to verify that the electronic function
    switch, effectively switches the optical output between the cross and bar states of the optical transmission function.

    For the corresponding switch model:

    Let's assume a switch model unitary. For a given 2x2 input optical switch "X". In bar state, in dual rail, transforms an optical input:
    ```
    .. raw::

        [[1] ----> [[1]
        [0]]        [0]]

    In cross state, in dual rail, transforms an optical input:

    .. raw::

        [[1] ----> [[0]
        [0]]        [1]]

    However, sometimes it is easier to describe a photonic logic transformation based on these states, rather than inherently
    the numerical phase that is applied. This may be the case, for example, in asymmetric Mach-Zehnder modulators models, etc.

    As such, this function will help us extract the corresponding phase for a particular switch transition.
    """
    state_phase_transition_list = get_state_phase_transitions(
        switch_function=switch_function,
        switch_states=switch_states,
        input_fock_states=input_fock_states,
        mode_amount=mode_amount,
        **kwargs,
    )
    # TODO implement the extraction from mapping the target fock states to the corresponing phase in more generic way
    cross_phase = extract_phase(state_phase_transition_list, transition_type="cross")
    bar_phase = extract_phase(state_phase_transition_list, transition_type="bar")
    return bar_phase, cross_phase
