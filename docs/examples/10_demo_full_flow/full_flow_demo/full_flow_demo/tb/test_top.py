# This file is public domain, it can be freely copied without restrictions.
# SPDX-License-Identifier: CC0-1.0
import cocotb
from cocotb.triggers import Timer
from cocotb.utils import get_sim_time
import pandas as pd


@cocotb.test()
async def truth_table_test(dut):
    """Test for logic defined by the truth table"""

    detector_in_data = []
    phase_map_out_data = []
    time_data = []

    # Test case 1
    dut.detector_in.value = bytes("00", "utf-8")
    await Timer(2, units="ns")

    assert dut.phase_map_out.value == bytes(
        "00", "utf-8"
    ), f"Test failed for inputs ['detector_in']: expected 00 but got {dut.phase_map_out.value}"
    detector_in_data.append(dut.detector_in.value)
    phase_map_out_data.append(dut.phase_map_out.value)
    time_data.append(get_sim_time())

    # Test case 2
    dut.detector_in.value = bytes("01", "utf-8")
    await Timer(2, units="ns")

    assert dut.phase_map_out.value == bytes(
        "10", "utf-8"
    ), f"Test failed for inputs ['detector_in']: expected 10 but got {dut.phase_map_out.value}"
    detector_in_data.append(dut.detector_in.value)
    phase_map_out_data.append(dut.phase_map_out.value)
    time_data.append(get_sim_time())

    # Test case 3
    dut.detector_in.value = bytes("10", "utf-8")
    await Timer(2, units="ns")

    assert dut.phase_map_out.value == bytes(
        "11", "utf-8"
    ), f"Test failed for inputs ['detector_in']: expected 11 but got {dut.phase_map_out.value}"
    detector_in_data.append(dut.detector_in.value)
    phase_map_out_data.append(dut.phase_map_out.value)
    time_data.append(get_sim_time())

    # Test case 4
    dut.detector_in.value = bytes("11", "utf-8")
    await Timer(2, units="ns")

    assert dut.phase_map_out.value == bytes(
        "11", "utf-8"
    ), f"Test failed for inputs ['detector_in']: expected 11 but got {dut.phase_map_out.value}"
    detector_in_data.append(dut.detector_in.value)
    phase_map_out_data.append(dut.phase_map_out.value)
    time_data.append(get_sim_time())

    simulation_data = {
        "detector_in": detector_in_data,
        "phase_map_out": phase_map_out_data,
        "time": time_data,
    }

    pd.DataFrame(simulation_data).to_csv(
        "/home/daquintero/phd/piel_private/docs/examples/10_demo_full_flow/full_flow_demo/full_flow_demo/tb/out/truth_table_test_results.csv"
    )
