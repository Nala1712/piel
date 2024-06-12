import numpy as np
from ....types import BitFormatType


def bits_array_from_bits_amount(
    bits_amount: int,
    bit_format: BitFormatType = "int",
) -> np.ndarray:
    """
    Returns an array of bits from a given amount of bits.

    Args:
        bits_amount(int): Amount of bits to generate.
        bit_format(str): Format of the bits to generate.

    Returns:
        bit_array(np.ndarray): Array of bits.
    """
    maximum_integer_represented = 2 ** (bits_amount)
    int_array = np.arange(maximum_integer_represented)
    bit_array = np.vectorize(np.base_repr)(int_array)
    if bit_format == "int":
        pass
    elif bit_format == "str":
        # Add leading zeros to bit strings
        bit_array = np.vectorize(lambda x: x.zfill(bits_amount))(bit_array)
    return bit_array
