# # Basic Interconnection Modelling
#
# It is very difficult to design an electronic-photonic system without actually *connecting* them together. As it turns out, interconnection modelling is crucial in understanding the scaling of these systems.
#
# We might want to model:
#
# - Interconnection effects of electro-optic switches with their transmission line, or transmission lines towards RF analog modulation
# - Path-length matched digital transmission lines to an amplifier
# - The transmission line from a detector diode to the low-noise amplifier before an analogue-to-digital converter.
# - Electronic to photonic chip bonding.
#
# An important aspect to note is that the computational architecture is designed to have the minimal amouunt of operations being computed for a given type of modelling, and this means the modelling speed is as fast as can be for a given operation within a python implementation, pending further toolset implementations.
#
# As such, understanding interconnection effects turns out to be pretty important in these type of systems.

from piel.models.physical.electrical.cable import (
    calculate_coaxial_cable_geometry,
    calculate_coaxial_cable_heat_transfer,
    calculate_dc_cable_geometry,
)
from piel.types.electrical import (
    CoaxialCableMaterialSpecificationType,
)

# ## Basic Thermal Modelling

# ### Modelling a DC Wire
#
# Let's take the most basic example to physically verify that the numerical functional implementation gives accurate results in terms of calculating the corresponding heat transfer. We will also do some analytical comparisons:

basic_dc_cable = calculate_dc_cable_geometry(
    length_m=1,
    core_diameter_m=1e-3,
)
basic_dc_cable

# ### Modelling a Coaxial Cable
#
# #### Thermal Heat Transfer
#
# Note that we have strongly-typed classes in order to manage the files containers across multiple functions. This enables flexibly extending the corresponding implementations.

basic_coaxial_cable = calculate_coaxial_cable_geometry(
    length_m=1,
    sheath_top_diameter_m=1.651e-3,
    sheath_bottom_diameter_m=1.468e-3,
    core_diameter_m=2e-3,
)
basic_coaxial_cable

# ```
# CoaxialCableGeometryType(core_cross_sectional_area_m2=3.141592653589793e-06, length_m=1.0, sheath_cross_sectional_area_m2=4.482872075095052e-07, total_cross_sectional_area_m2=3.5898798610992983e-06)
# ```

# You can also run the help function to learn more of the corresponding class, on top of the existing documentation.

# +
# help(CoaxialCableGeometryType)
# -

# Now, let's apply each section with materials. First, let's work out what are all the current supported materials specifications (feel free to contribute!). Note that this is always specific to the corresponding property.

from piel.materials.thermal_conductivity import (
    material_references as thermal_conductivity_material_references,
)

thermal_conductivity_material_references

# ```
# [('stainless_steel', '304'),
#  ('stainless_steel', '310'),
#  ('stainless_steel', '316'),
#  ('aluminum', '1100'),
#  ('copper', 'rrr50'),
#  ('copper', 'rrr100'),
#  ('copper', 'rrr150'),
#  ('copper', 'rrr300'),
#  ('copper', 'rrr500'),
#  ('teflon', None)]
# ```

# It is pretty straightforward to define a corresponding coaxial-cable material specification accordingly with the static `CoaxialCableMaterialSpecificationType` container:

basic_coaxial_cable_materials = CoaxialCableMaterialSpecificationType(
    core=("copper", "rrr50"), sheath=("copper", "rrr50"), dielectric=("teflon", None)
)
basic_coaxial_cable_materials

# ```
# CoaxialCableMaterialSpecificationType(core=('copper', 'rrr50'), sheath=('copper', 'rrr50'), dielectric=('teflon', None))
# ```

# Now, let's assume we have a coaxial cable that goes from room temperature to cryogenic temperatures. Say, a cable inside a cryostat that goes from 273K to 70K. Let's work out how much thermal heat transfer occurs in between these stages in Watts.

temperature_range_limits_K = tuple([70, 273])

basic_coaxial_cable_heat_transfer = calculate_coaxial_cable_heat_transfer(
    temperature_range_K=temperature_range_limits_K,
    geometry_class=basic_coaxial_cable,
    material_class=basic_coaxial_cable_materials,
)
basic_coaxial_cable_heat_transfer

# ```
# CoaxialCableHeatTransferType(core=0.0019091610845816964, sheath=0.0019091610845816964, dielectric=0.00018867678408072714, total=0.00400699895324412)
# ```

# ### Larger System Modelling

# Modelling the heat transfer of multiple coaxial cables in parallel in a system involves basic python operations:s

parallel_cables_amount = 4
4 * basic_coaxial_cable_heat_transfer.total

# ```
# 0.01602799581297648
# ```

# Modelling the heat transfer of 4 cables in series, just involves making the cable in series:

# +
basic_coaxial_cable_4_in_series = calculate_coaxial_cable_geometry(
    length_m=1 * 4,
    sheath_top_diameter_m=1.651e-3,
    sheath_bottom_diameter_m=1.468e-3,
    core_diameter_m=2e-3,
)

basic_coaxial_cable_heat_transfer_4_in_series = calculate_coaxial_cable_heat_transfer(
    temperature_range_K=temperature_range_limits_K,
    geometry_class=basic_coaxial_cable_4_in_series,
    material_class=basic_coaxial_cable_materials,
)
basic_coaxial_cable_heat_transfer_4_in_series
# -

# ```
# CoaxialCableHeatTransferType(core=0.0004772902711454241, sheath=0.0004772902711454241, dielectric=4.7169196020181784e-05, total=0.00100174973831103)
# ```

# ## Basic RF Modelling and Experimental Relationships

# In the following section of this example, we will explore some basic principles of RF transmission line measurements in the context of both experimental measurements and larger system modelling. We will really explore some basic RF principles and how these can be represented with open-source toolsets using `piel`.
#
# A very common package to model radio-frequency systems in python is called [`scikit-rf`](https://scikit-rf.readthedocs.io/en/latest/index.html). Particularly, it has a lot of useful functionality to translate IO files directly from common measurement standards in a format that is useful for device characterization and modelling. We will explore some basic situations commonly used throughout modelling `rf-photonic` systems.
#
# As far as I can tell from basic usage, the only useful files are `.s2p` Touchstone files for trace measurments, and `.cti` files for calibration/instrument settings storage. We will use `.s2p` files throughout primarily.

import skrf
from skrf.io.touchstone import hfss_touchstone_2_network

# ### De-Embedding Measurements & Calibration

# A very common procedure when doing a measurement with a vector-network-analyser (VNA) is to perform calibration, also called de-embedding. This is to move the measurement plane from the VNA up to the device-under-test (DUT) and is necessary for accurate measurements of our devices.
#
# Alongside the equipment calibration manual, some good references about this are:
#
# 1. Lourandakis, E. (2016). On-wafer microwave measurements and de-embedding. Artech House.
# 2. Pozar, D. M. (2000). Microwave and RF design of wireless systems. John Wiley & Sons.

# <figure>
# <img src="../../_static/img/examples/08_basic_interconnection_modelling/experimental_calibration.jpg" alt="drawing" width="70%"/>
# <figcaption align = "center"> YOUR CAPTION </figcaption>
# </figure>


# ### Frequency-Domain Measurement of a 50$\Omega$ Terminator

# <figure>
# <img src="../../_static/img/examples/08_basic_interconnection_modelling/experimental_open_terminator.jpg" alt="drawing" width="70%"/>
# <figcaption align = "center"> This plot contains the S11 logarithmic magnitude and phase of a 50 $\Omega$ terminator. Note that the second port is unplugged so all the S22 files is irrelevant.</figcaption>
# </figure>

measured_terminator_data_file = "measurement_data/terminator.s2p"
terminator_network = hfss_touchstone_2_network(measured_terminator_data_file)
terminator_network

terminator_network.plot_s_mag()

terminator_network.plot_s_db()

# +
# dir(terminator_network)
# -

# TODO what is the plot below.

terminator_network.plot_s_time()

# ###  Frequency-Domain Measurement of a Coaxial Cable

# A coaxial cable is a transmission line, which means it has a signal transmission associated with it for a range of RF frequencies. We might want to explore how the attentuation and reflection of our high-frequency signals operate. Let's understand some network theory basics in relation to an actual experimental context.
#
# In this example, we will consider the experimental PNA network measurement of a [141-1MSM+](https://www.minicircuits.com/WebStore/dashboard.html?model=141-1MSM%2B) cable and compare it to some network theory.
#
# Note that it is important to know the fundamental limits of the measurement. For example, for an SMA 3.5mm network, the bandwidth is inherently limited to 18-24.5 GHz.

# This are some performance metrics of this cable as described by the [datasheet](https://www.minicircuits.com/pdfs/141-1MSM+.pdf):
#
# ![rf_plots_1411MSM](../../_static/img/examples/08_basic_interconnection_modelling/rf_plots_1411MSM.png)

# +
import pandas as pd
import matplotlib.pyplot as plt

# 141-1MSM+ cable datasheet model
data = {
    "frequency_mhz": [
        100.0,
        200.0,
        300.0,
        400.0,
        500.0,
        600.0,
        700.0,
        800.0,
        900.0,
        1000.0,
        1100.0,
        1250.0,
        1500.0,
        1750.0,
        2000.0,
        2250.0,
        2500.0,
        2750.0,
        3000.0,
        3250.0,
        3500.0,
        3750.0,
        4000.0,
        4250.0,
        4500.0,
        5000.0,
        5500.0,
        6000.0,
        6500.0,
        7000.0,
        7500.0,
        8000.0,
        8500.0,
        9000.0,
        9500.0,
        10000.0,
        11000.0,
        12000.0,
        13000.0,
        13500.0,
        14000.0,
        14500.0,
        15000.0,
        15500.0,
        16000.0,
        16500.0,
        17000.0,
        17500.0,
        18000.0,
    ],
    "insertion_loss_db": [
        0.12,
        0.18,
        0.21,
        0.26,
        0.28,
        0.31,
        0.34,
        0.40,
        0.43,
        0.46,
        0.44,
        0.47,
        0.52,
        0.55,
        0.62,
        0.63,
        0.66,
        0.70,
        0.74,
        0.77,
        0.80,
        0.84,
        0.87,
        0.90,
        0.93,
        0.99,
        1.05,
        1.10,
        1.15,
        1.20,
        1.25,
        1.30,
        1.35,
        1.40,
        1.45,
        1.49,
        1.58,
        1.67,
        1.75,
        1.81,
        1.85,
        1.90,
        1.92,
        1.97,
        2.04,
        2.07,
        2.11,
        2.16,
        2.21,
    ],
    "return_loss_db_male1": [
        44.6,
        40.1,
        36.7,
        33.9,
        33.5,
        32.4,
        31.9,
        30.3,
        30.2,
        31.8,
        35.7,
        31.2,
        37.7,
        36.0,
        33.3,
        48.7,
        42.0,
        40.5,
        43.9,
        37.1,
        40.4,
        47.1,
        41.5,
        35.4,
        40.2,
        36.4,
        38.5,
        35.8,
        40.9,
        37.6,
        38.4,
        35.8,
        31.9,
        45.3,
        30.5,
        42.2,
        35.1,
        28.1,
        34.3,
        25.3,
        24.8,
        26.5,
        30.2,
        26.0,
        23.6,
        27.6,
        23.5,
        23.2,
        21.8,
    ],
    "return_loss_db_male2": [
        53.6,
        46.1,
        42.2,
        38.3,
        37.6,
        36.7,
        36.3,
        35.9,
        35.4,
        35.3,
        37.5,
        36.5,
        55.5,
        38.2,
        38.0,
        46.6,
        44.2,
        43.1,
        46.5,
        38.1,
        48.5,
        45.0,
        39.7,
        43.6,
        40.4,
        39.7,
        36.3,
        34.5,
        41.2,
        39.1,
        36.8,
        34.1,
        31.5,
        37.3,
        28.3,
        42.3,
        36.8,
        29.2,
        43.9,
        29.3,
        25.9,
        23.5,
        32.7,
        27.2,
        22.4,
        25.8,
        23.6,
        22.7,
        22.5,
    ],
}

# Create a DataFrame
df = pd.DataFrame(data)
plt.plot(df.frequency_mhz, -df.insertion_loss_db)
plt.plot(df.frequency_mhz, -df.return_loss_db_male1)
# -

# <figure>
# <img src="../../_static/img/examples/08_basic_interconnection_modelling/experimental_coax.jpg" alt="drawing" width="70%"/>
# <figcaption align = "center"> YOUR CAPTION </figcaption>
# </figure>
#
#
#

measured_mid_resolution_14111msm_data_file = "measurement_data/mid_res_1411msm_cal1.s2p"
mid_resolution_14111msm_network = hfss_touchstone_2_network(
    measured_mid_resolution_14111msm_data_file
)
mid_resolution_14111msm_network

mid_resolution_14111msm_network.plot_s_db()

measured_high_resolution_14111msm_data_file = (
    "measurement_data/high_res_1411msm_cal1.s2p"
)
high_resolution_14111msm_network = hfss_touchstone_2_network(
    measured_high_resolution_14111msm_data_file
)
high_resolution_14111msm_network

high_resolution_14111msm_network.plot_s_db()

# ###  Post-Calibration Frequency-Domain Measurement

calibrated_14111msm_data_file = "measurement_data/1411msm_cal2.s2p"
calibrated_14111msm_network = hfss_touchstone_2_network(calibrated_14111msm_data_file)
calibrated_14111msm_network

calibrated_14111msm_network.plot_s_db()

#