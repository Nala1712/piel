from ..tools.amaranth.types import TruthTable
from ..file_system import return_path
from ..types import PathTypes


def create_cocotb_truth_table_verification_python_script(
    module: PathTypes,
    truth_table: TruthTable,
    test_python_module_name: str = "top_test",
):
    """
    Creates a cocotb test script for verifying logic defined by the truth table.

    Args:
        module (PathTypes): The path to the module where the test script will be placed.
        truth_table (TruthTable): A dictionary representing the truth table.
        test_python_module_name (str, optional): The name of the test python module. Defaults to "top_test".

    Example:
        truth_table = {
            "A": [0, 0, 1, 1],
            "B": [0, 1, 0, 1],
            "X": [0, 1, 1, 0]  # Expected output (for XOR logic, as an example)
        }
        create_cocotb_truth_table_verification_python_script(truth_table)
    """
    # Resolve the module path and create the tb directory if it doesn't exist
    module_path = return_path(module)
    tb_directory_path = module_path / "tb"
    python_module_test_file_path = tb_directory_path / f"{test_python_module_name}.py"
    output_file = tb_directory_path / "out" / "truth_table_test_results.csv"

    # Create the header for the script
    script_content = """
# This file is public domain, it can be freely copied without restrictions.
# SPDX-License-Identifier: CC0-1.0
import cocotb
from cocotb.triggers import Timer
from cocotb.utils import get_sim_time
import pandas as pd

@cocotb.test()
async def truth_table_test(dut):
    \"\"\"Test for logic defined by the truth table\"\"\"

"""
    # Extract signal names and values from the truth table
    signals = list(truth_table.keys())
    num_tests = len(truth_table[signals[0]])

    # Initialize lists to store signal data for logging
    for signal in signals:
        script_content += f"    {signal.lower()}_data = []\n"

    script_content += "    time_data = []\n\n"

    # Loop over each row in the truth table to generate test cases
    for i in range(num_tests):
        script_content += f"    # Test case {i + 1}\n"
        for signal in signals[:-1]:  # All but the last signal are inputs
            value = truth_table[signal][i]
            script_content += f"    dut.{signal}.value = bytes(\"{value}\", 'utf-8')\n"  # Assign binary string values directly

        script_content += "    await Timer(2, units='ns')\n\n"

        expected_output = truth_table[signals[-1]][
            i
        ]  # The last signal is the expected output
        output_signal = signals[-1]

        # Add assertion and logging
        script_content += f"    assert dut.{output_signal}.value == bytes(\"{expected_output}\", 'utf-8'), "
        script_content += f'f"Test failed for inputs {signals[:-1]}: expected {expected_output} but got {{dut.{output_signal}.value}}"\n'

        for signal in signals:
            script_content += f"    {signal.lower()}_data.append(dut.{signal}.value)\n"

        script_content += "    time_data.append(get_sim_time())\n\n"

    # Store the results in a CSV file
    script_content += "    simulation_data = {\n"
    for signal in signals:
        script_content += f'        "{signal.lower()}": {signal.lower()}_data,\n'
    script_content += '        "time": time_data\n'
    script_content += "    }\n\n"
    script_content += (
        f'    pd.DataFrame(simulation_data).to_csv("{str(output_file)}") \n'
    )

    # Write the script to a file
    with open(python_module_test_file_path, "w") as file:
        file.write(script_content)

    print(f"Test script written to {python_module_test_file_path}")
