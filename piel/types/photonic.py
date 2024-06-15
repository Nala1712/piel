import gdsfactory as gf
import sax
from .core import ArrayTypes

PortsTuple = tuple[str, ...]
SParameterMatrixTuple = tuple[ArrayTypes, PortsTuple]

OpticalTransmissionCircuit = sax.saxtypes.Callable
RecursiveNetlist = sax.RecursiveNetlist
PhotonicCircuitComponent = gf.Component
