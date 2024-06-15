from typing import Literal, Optional
from typing_extensions import TypedDict
import pandas as pd
from pydantic import ConfigDict
from .core import TupleIntType, TupleFloatType, PielBaseModel

PhaseMapType = TupleFloatType | TupleIntType

class FockStatePhaseTransitionType(TypedDict):

    phase: PhaseMapType
    input_fock_state: TupleIntType
    output_fock_state: TupleIntType
    target_mode_output: Optional[bool | int]


"""
This is the standard format of a corresponding output state for a given input state in the electro-optic model:

output_state_0 = {
    "phase": (switch_states[0],),
    "input_fock_state": piel.convert_array_type(valid_input_fock_states[0], "tuple"),
    "output_fock_state": piel.absolute_to_threshold(raw_output_state_0, output_array_type="tuple"),
}
"""


PhaseTransitionTypes = Literal["cross", "bar"]


class OpticalStateTransitions(PielBaseModel):

    model_config = ConfigDict(extra="allow")

    mode_amount: int
    target_mode_index: int
    transmission_data: list[FockStatePhaseTransitionType]

    @property
    def transition_dataframe(self):
        return pd.DataFrame(self.transmission_data)

    @property
    def target_output_dataframe(self):
        # TODO add verification eventually
        return self.transition_dataframe[
            self.transition_dataframe["target_mode_output"] == 1
        ]
