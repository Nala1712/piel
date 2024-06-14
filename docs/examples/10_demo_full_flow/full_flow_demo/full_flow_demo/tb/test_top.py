# This file is public domain, it can be freely copied without restrictions.
# SPDX-License-Identifier: CC0-1.0
import cocotb
from cocotb.triggers import Timer
from cocotb.utils import get_sim_time
import pandas as pd


@cocotb.test()
async def truth_table_test(dut):
    """Test for logic defined by the truth table"""

    input_fock_state_data = []
    phase_bit_data = []
    time_data = []

    # Test case 1
    dut.input_fock_state.value = cocotb.binary.BinaryValue("100")
    await Timer(2, units="ns")

    assert dut.phase_bit.value == cocotb.binary.BinaryValue(
        "0000000000"
    ), f"Test failed for inputs ['input_fock_state']: expected 0000000000 but got {dut.phase_bit.value}."
    input_fock_state_data.append(dut.input_fock_state.value)
    phase_bit_data.append(dut.phase_bit.value)
    time_data.append(get_sim_time())

    # Test case 2
    dut.input_fock_state.value = cocotb.binary.BinaryValue("001")
    await Timer(2, units="ns")

    assert dut.phase_bit.value == cocotb.binary.BinaryValue(
        "1111100000"
    ), f"Test failed for inputs ['input_fock_state']: expected 1111100000 but got {dut.phase_bit.value}."
    input_fock_state_data.append(dut.input_fock_state.value)
    phase_bit_data.append(dut.phase_bit.value)
    time_data.append(get_sim_time())

    # Test case 3
    dut.input_fock_state.value = cocotb.binary.BinaryValue("010")
    await Timer(2, units="ns")

    assert dut.phase_bit.value == cocotb.binary.BinaryValue(
        "0000011111"
    ), f"Test failed for inputs ['input_fock_state']: expected 0000011111 but got {dut.phase_bit.value}."
    input_fock_state_data.append(dut.input_fock_state.value)
    phase_bit_data.append(dut.phase_bit.value)
    time_data.append(get_sim_time())

    # Test case 4
    dut.input_fock_state.value = cocotb.binary.BinaryValue("001")
    await Timer(2, units="ns")

    assert dut.phase_bit.value == cocotb.binary.BinaryValue(
        "1111100000"
    ), f"Test failed for inputs ['input_fock_state']: expected 1111100000 but got {dut.phase_bit.value}."
    input_fock_state_data.append(dut.input_fock_state.value)
    phase_bit_data.append(dut.phase_bit.value)
    time_data.append(get_sim_time())

    simulation_data = {
        "input_fock_state": input_fock_state_data,
        "phase_bit": phase_bit_data,
        "time": time_data,
    }

    pd.DataFrame(simulation_data).to_csv(
        "/home/daquintero/phd/piel_private/docs/examples/10_demo_full_flow/full_flow_demo/full_flow_demo/tb/out/truth_table_test_results.csv"
    )
