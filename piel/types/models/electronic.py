from piel.types import PielBaseModel
from typing import Optional

MinimumMaximumType = tuple([Optional[float], Optional[float]])


class LNAMetricsType(PielBaseModel):
    """
    Low-noise amplifier metrics.
    """

    footprint_mm2: Optional[float]
    bandwidth_Hz: MinimumMaximumType or None
    noise_figure: MinimumMaximumType or None
    power_consumption_mW: MinimumMaximumType or None
    power_gain_dB: MinimumMaximumType or None
    supply_voltage_V: Optional[float]
    technology_nm: Optional[float]
    technology_material: Optional[str]


class HVAMetricsType(PielBaseModel):
    """
    High-voltage amplifier metrics.
    """

    footprint_mm2: Optional[float]
    bandwidth_Hz: MinimumMaximumType or None
    power_added_efficiency: MinimumMaximumType or None
    power_consumption_mW: MinimumMaximumType or None
    power_gain_dB: MinimumMaximumType or None
    saturated_power_output_dBm: Optional[float]
    supply_voltage_V: Optional[float]
    technology_nm: Optional[float]
    technology_material: Optional[str]
