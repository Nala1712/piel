# # `piel` Electronic-Photonic Co-Design - Full Flow Demo

# The goal of this notebook is to demonstrate some of the codesign functionality in a photonics-first electronically-specified system.

# ## 1. Setting up our electro-optic photonic system
#
# Let's first extract the digital logic we want to implement from a basic chained electro-optic switch fabric.

# +
# We begin by importing a parametric circuit from `gdsfactory`:
import gdsfactory as gf
from piel.models.physical.photonic import (
    mzi2x2_2x2_phase_shifter,
    component_lattice_generic,
)
import numpy as np
import jax.numpy as jnp
import piel
import sax

from gdsfactory.generic_tech import get_generic_pdk

PDK = get_generic_pdk()
PDK.activate()


# -


def create_switch_fabric():
    # CURRENT TODO: Create a basic chain fabric and verify the logic is implemented properly with binary inputs.

    chain_3_mode_lattice = [
        [mzi2x2_2x2_phase_shifter(), 0],
        [0, mzi2x2_2x2_phase_shifter()],
    ]

    chain_3_mode_lattice_circuit = component_lattice_generic(
        network=chain_3_mode_lattice,
    )
    return chain_3_mode_lattice_circuit


create_switch_fabric()

# ## 2. Extracting our optical-to-electronic control logic truth table


# ## 3. Synthesizing the logic, digtial testing and layout implementation

# +
from piel.tools.amaranth import (
    construct_amaranth_module_from_truth_table,
    generate_verilog_from_amaranth,
    verify_truth_table,
)

detector_phase_truth_table = {
    "detector_in": ["00", "01", "10", "11"],
    "phase_map_out": ["00", "10", "11", "11"],
}

input_ports_list = ["detector_in"]
output_ports_list = ["phase_map_out"]
our_truth_table_module = construct_amaranth_module_from_truth_table(
    truth_table=detector_phase_truth_table,
    inputs=input_ports_list,
    outputs=output_ports_list,
)

ports_list = input_ports_list + output_ports_list
generate_verilog_from_amaranth(
    amaranth_module=our_truth_table_module,
    ports_list=ports_list,
    target_file_name="our_truth_table_module.v",
    target_directory=".",
)

design_directory = piel.return_path(amaranth_driven_flow)

amaranth_driven_flow_src_folder = piel.get_module_folder_type_location(
    module=amaranth_driven_flow, folder_type="digital_source"
)

ports_list = input_ports_list + output_ports_list
generate_verilog_from_amaranth(
    amaranth_module=our_truth_table_module,
    ports_list=ports_list,
    target_file_name="our_truth_table_module.v",
    target_directory=amaranth_driven_flow_src_folder,
)

verify_truth_table(
    truth_table_amaranth_module=our_truth_table_module,
    truth_table_dictionary=detector_phase_truth_table,
    inputs=input_ports_list,
    outputs=output_ports_list,
    vcd_file_name="our_truth_table_module.vcd",
    target_directory=".",
)
# -

# ## 3a. Modelling our implementing digital-to-optical logic

# +
design_directory = piel.return_path(simple_design)
source_output_files_directory = (
    piel.get_module_folder_type_location(
        module=simple_design, folder_type="digital_source"
    )
    / "out"
)
simulation_output_files_directory = (
    piel.get_module_folder_type_location(
        module=simple_design, folder_type="digital_testbench"
    )
    / "out"
)


piel.configure_cocotb_simulation(
    design_directory=simple_design,
    simulator="icarus",
    top_level_language="verilog",
    top_level_verilog_module="adder",
    test_python_module="test_adder",
    design_sources_list=list((design_directory / "src").iterdir()),
)

# Run cocotb simulation
piel.run_cocotb_simulation(design_directory)

cocotb_simulation_output_files = piel.get_simulation_output_files_from_design(
    simple_design
)
cocotb_simulation_output_files

example_simple_simulation_data = piel.read_simulation_data(
    cocotb_simulation_output_files[0]
)
example_simple_simulation_data

piel.simple_plot_simulation_data(example_simple_simulation_data)
# TODO fix this properly.

cocotb_simulation_output_files = piel.get_simulation_output_files_from_design(
    simple_design
)
example_simple_simulation_data = piel.read_simulation_data(
    cocotb_simulation_output_files[0]
)
example_simple_simulation_data

basic_ideal_phase_array = (
    piel.models.logic.electro_optic.return_phase_array_from_data_series(
        data_series=example_simple_simulation_data.x, phase_map=basic_ideal_phase_map
    )
)

example_simple_simulation_data["phase"] = basic_ideal_phase_array
example_simple_simulation_data

our_custom_library = piel.models.frequency.compose_custom_model_library_from_defaults(
    {"straight_heater_metal_undercut": straight_heater_metal_simple}
)
our_custom_library

mzi2x2_model, mzi2x2_model_info = sax.circuit(
    netlist=mzi2x2_2x2_phase_shifter_netlist, models=our_custom_library
)
piel.sax_to_s_parameters_standard_matrix(mzi2x2_model(), input_ports_order=("o2", "o1"))

mzi2x2_active_unitary_array = list()
for phase_i in example_simple_simulation_data.phase:
    mzi2x2_active_unitary_i = piel.sax_to_s_parameters_standard_matrix(
        mzi2x2_model(sxt={"active_phase_rad": phase_i}),
        input_ports_order=(
            "o2",
            "o1",
        ),
    )
    mzi2x2_active_unitary_array.append(mzi2x2_active_unitary_i)

optical_port_input = np.array([1, 0])
optical_port_input

example_optical_power_output = np.dot(
    mzi2x2_simple_simulation_data.unitary.iloc[0][0], optical_port_input
)
example_optical_power_output

output_amplitude_array_0 = np.array([])
output_amplitude_array_1 = np.array([])
for unitary_i in mzi2x2_simple_simulation_data.unitary:
    output_amplitude_i = np.dot(unitary_i[0], optical_port_input)
    output_amplitude_array_0 = np.append(
        output_amplitude_array_0, output_amplitude_i[0]
    )
    output_amplitude_array_1 = np.append(
        output_amplitude_array_1, output_amplitude_i[1]
    )
output_amplitude_array_0

mzi2x2_simple_simulation_data["output_amplitude_array_0"] = output_amplitude_array_0
mzi2x2_simple_simulation_data["output_amplitude_array_1"] = output_amplitude_array_1
mzi2x2_simple_simulation_data

mzi2x2_simple_simulation_data_lines = piel.visual.points_to_lines_fixed_transient(
    data=mzi2x2_simple_simulation_data,
    time_index_name="t",
    fixed_transient_time=1,
)

simple_ideal_o3_mzi_2x2_plots = piel.visual.plot_simple_multi_row(
    data=mzi2x2_simple_simulation_data_lines,
    x_axis_column_name="t",
    row_list=[
        "phase",
        "output_amplitude_array_0_abs",
        "output_amplitude_array_0_phase_deg",
    ],
    y_axis_title_list=["e1 Phase", "o3 Amplitude", "o3 Phase"],
)
simple_ideal_o3_mzi_2x2_plots.savefig(
    "../_static/img/examples/03a_sax_active_cosimulation/simple_ideal_o3_mzi_2x2_plots.PNG"
)
# -

# ## 3b. Digital Chip Implementation

# +
from piel.integration.amaranth_openlane import (
    layout_amaranth_truth_table_through_openlane,
)

layout_amaranth_truth_table_through_openlane(
    amaranth_module=our_truth_table_module,
    inputs_name_list=input_ports_list,
    outputs_name_list=output_ports_list,
    parent_directory=amaranth_driven_flow,
    openlane_version="v1",
)
# -

# ## 4a. Driver-Amplfier Modelling

# +
# toddo add here the example of a simulated spice device.
# -

# ## 4b. Composing and Equivalent-Circuit Modelling

# +
from piel.models.physical.photonic import (
    mzi2x2_2x2_phase_shifter,
    straight_heater_metal_simple,
)
import hdl21 as h
import pandas as pd
import numpy as np
import piel
import sax
import sys
from gdsfactory.generic_tech import get_generic_pdk

our_resistive_heater_netlist = straight_heater_metal_simple().get_netlist(
    allow_multiple=True, exclude_port_types="optical"
)
# our_resistive_mzi_2x2_2x2_phase_shifter_netlist = our_resistive_mzi_2x2_2x2_phase_shifter.get_netlist(exclude_port_types="optical")
# our_resistive_heater_netlist

our_resistive_heater_spice_netlist = piel.gdsfactory_netlist_with_hdl21_generators(
    our_resistive_heater_netlist
)
our_resistive_heater_spice_netlist


@h.module
class TransientTb:
    """# Basic Extracted Device DC Operating Point Testbench"""

    VSS = h.Port()  # The testbench interface: sole port VSS - GROUND
    VPULSE = h.Vpulse(
        delay=1 * h.prefix.m,
        v1=-1000 * h.prefix.m,
        v2=1000 * h.prefix.m,
        period=100 * h.prefix.m,
        rise=10 * h.prefix.m,
        fall=10 * h.prefix.m,
        width=75 * h.prefix.m,
    )(
        n=VSS
    )  # A configured voltage pulse source

    # Our component under test
    dut = example_straight_resistor()
    dut.e1 = VPULSE.p
    dut.e2 = VSS


simple_transient_simulation = piel.configure_transient_simulation(
    testbench=TransientTb,
    stop_time_s=200e-3,
    step_time_s=1e-4,
    name="simple_transient_simulation",
)
simple_transient_simulation

piel.run_simulation(simple_transient_simulation, to_csv=True)

transient_simulation_results = pd.read_csv("TransientTb.csv")
transient_simulation_results.iloc[20:40]
# -

# ## 5. What comes next?
