import amaranth as am
from typing import Literal
from piel.types.digital import TruthTable, LogicSignalsList

__all__ = ["construct_amaranth_module_from_truth_table"]

def construct_amaranth_module_from_truth_table(
    truth_table: TruthTable,
    implementation_type: Literal[
        "combinatorial", "sequential", "memory"
    ] = "combinatorial",
):
    """
    This function implements a truth table as a module in amaranth,
    Note that in some form in amaranth each statement is a form of construction.

    The truth table is in the form of:

        detector_phase_truth_table = {
            "detector_in": ["00", "01", "10", "11"],
            "phase_map_out": ["00", "10", "11", "11"],
        }

    Args:
        truth_table (TruthTable): The truth table in the form of a TruthTable object.
        implementation_type (Literal["combinatorial", "sequential", "memory"], optional): The type of implementation. Defaults to "combinatorial".

    Returns:
        Generated amaranth module.
    """

    # Extract inputs and outputs from the truth table
    inputs = truth_table.input_ports
    outputs = truth_table.output_ports
    truth_table_dict = truth_table.implementation_dictionary

    class TruthTableModule(am.Elaboratable):
        def __init__(self, truth_table: dict, inputs: list, outputs: list):
            super(TruthTableModule, self).__init__()

            # Ensure that the truth table has entries
            if len(truth_table[inputs[0]]) == 0:
                raise ValueError("No truth table inputs provided." + str(inputs))

            # Initialize signals for input and output ports and assign them as attributes
            self.input_signal = am.Signal(len(truth_table[inputs[0]][0]), name=inputs[0])
            self.output_signals = {output: am.Signal(len(truth_table[output][0]), name=output) for output in outputs}

            # Assign input and output signals as class attributes for external access
            setattr(self, inputs[0], self.input_signal)
            for output in outputs:
                setattr(self, output, self.output_signals[output])

            self.inputs_names = inputs
            self.outputs_names = outputs
            self.truth_table = truth_table

        def elaborate(self, platform):
            m = am.Module()

            # Assume the truth table entries are consistent and iterate over them
            with m.Switch(self.input_signal):
                for i in range(len(self.truth_table[self.inputs_names[0]])):
                    input_case = str(self.truth_table[self.inputs_names[0]][i])
                    with m.Case(input_case):
                        # Assign values to each output signal for the current case
                        for output in self.outputs_names:
                            output_signal_value = self.output_signals[output].eq
                            m.d.comb += output_signal_value(int(self.truth_table[output][i], 2))

                # Default case: set all outputs to 0
                with m.Case():
                    for output in self.outputs_names:
                        m.d.comb += self.output_signals[output].eq(0)

            return m

    return TruthTableModule(truth_table_dict, inputs, outputs)
