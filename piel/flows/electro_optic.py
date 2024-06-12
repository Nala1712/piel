import gdsfactory as gf
import sax
from ..models.frequency.defaults import get_default_models


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
