from ..file_system import return_path
from ..project_structure import get_module_folder_type_location
from ..tools.amaranth import (
    construct_amaranth_module_from_truth_table,
    generate_verilog_from_amaranth,
    verify_truth_table,
    TruthTable,
    LogicSignals,
)
from ..types import PathTypes


def generate_verilog_and_verification_from_truth_table(
    truth_table: TruthTable,
    input_ports: LogicSignals,
    output_ports: LogicSignals,
    module: PathTypes,
    target_file_name: str = "truth_table_module",
):
    """
    Processes a truth table to generate an Amaranth module, converts it to Verilog,
    and creates a testbench for verification.

    Parameters:
    - truth_table (dict): The truth table defining the logic. It should be a dictionary where keys are
                          port names and values are lists of binary strings representing the truth table entries.
                          Example: {"detector_in": ["00", "01", "10", "11"], "phase_map_out": ["00", "10", "11", "11"]}
    - input_ports (list of str): A list of input port names that correspond to keys in the truth table.
                                 Example: ["detector_in"]
    - output_ports (list of str): A list of output port names that correspond to keys in the truth table.
                                  Example: ["phase_map_out"]
    - module (str): The name or path of the module within the design hierarchy where the generated files
                    will be placed. This is used to determine the file structure and directory paths.
                    Example: "full_flow_demo"
    - target_file_name (str): The verilog and vcd file name.

    Returns:
    - None

    Steps:
    1. Combines the input and output ports into a single list.
    2. Constructs an Amaranth module from the provided truth table.
    3. Determines the appropriate directory and source folder for the design.
    4. Generates a Verilog file from the Amaranth module.
    5. Creates a testbench to verify the generated module logic and produces a VCD file.

    Example:
    >>> detector_phase_truth_table = {
    >>>     "detector_in": ["00", "01", "10", "11"],
    >>>     "phase_map_out": ["00", "10", "11", "11"]
    >>> }
    >>> input_ports_list = ["detector_in"]
    >>> output_ports_list = ["phase_map_out"]
    >>> full_flow_demo = "full_flow_demo_module"
    >>> generate_verilog_and_verification_from_truth_table(detector_phase_truth_table,input_ports_list,output_ports_list,full_flow_demo)
    """

    # Combine input and output ports into a single list for ports
    ports_list = input_ports + output_ports

    # Construct Amaranth module from the truth table
    amaranth_module = construct_amaranth_module_from_truth_table(
        truth_table=truth_table,
        inputs=input_ports,
        outputs=output_ports,
    )

    # Determine the design directory
    design_directory = return_path(module)
    src_folder = get_module_folder_type_location(
        module=module, folder_type="digital_source"
    )

    # Generate Verilog file from the Amaranth module
    generate_verilog_from_amaranth(
        amaranth_module=amaranth_module,
        ports_list=ports_list,
        target_file_name=f"{target_file_name}.v",
        target_directory=src_folder,
    )

    # Create a testbench to verify the logic and generate a VCD file
    verify_truth_table(
        truth_table_amaranth_module=amaranth_module,
        truth_table_dictionary=truth_table,
        inputs=input_ports,
        outputs=output_ports,
        vcd_file_name=f"{target_file_name}.vcd",
        target_directory=module,
    )
