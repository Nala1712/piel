"""
This file provides a set of utilities in converting between common data types to represent information between different toolsets.
"""
import jax.numpy as jnp
import numpy as np
import qutip
from .core import ArrayTypes, PackageArrayType, TupleIntType


def convert_array_type(array: ArrayTypes, output_type: PackageArrayType):
    if output_type == "qutip":
        if type(array) is qutip.Qobj:
            pass
        else:
            array = qutip.Qobj(array)
    elif output_type == "jax":
        if type(array) is jnp.ndarray:
            pass
        else:
            array = jnp.array(array)
    elif output_type == "numpy":
        if type(array) is np.ndarray:
            pass
        else:
            array = np.array(array)
    elif output_type == "list":
        if type(array) is list:
            pass
        else:
            array = array.tolist()
    elif output_type == "tuple":
        if type(array) is tuple:
            pass
        else:
            array = tuple(array.tolist())
    elif output_type == TupleIntType:
        if isinstance(array, jnp.ndarray):
            array = tuple(array.tolist())

        if isinstance(array, tuple):
            # Check if the tuple is a tuple of integers
            if all(isinstance(i, int) for i in array):
                pass
            # if it is a tuple of lists, extract the first element of each list
            elif all(isinstance(i, list) for i in array):
                array = tuple(i[0] for i in array)
            else:
                raise ValueError("The tuple must be a tuple of integers.")
    else:
        raise ValueError("The output type must be either 'qutip' or 'jax'.")
    return array


def convert_2d_array_to_string(list_2D: list[list]):
    """
    This function is particularly useful to convert digital data when it is represented as a 2D array into a set of strings.

    Args:
        list_2D (list[list]): A 2D array of binary data.

    Returns:
        binary_string (str): A string of binary data.

    Usage:

        list_2D=[[0], [0], [0], [1]]
        convert_2d_array_to_string(list_2D)
        >>> "0001"
    """
    binary_string = "".join(str(sublist[0]) for sublist in list_2D)
    return binary_string


def absolute_to_threshold(
    array: ArrayTypes,
    threshold: float = 1e-6,
    dtype_output: int | float | bool = int,
    output_array_type: PackageArrayType = "jax",
) -> PackageArrayType:
    """
    This function converts the computed optical transmission arrays to single bit digital signals.
    The function takes the absolute value of the array and compares it to a threshold to determine the digital signal.

    Args:
        array (ArrayTypes): The optical transmission array of any dimension.
        dtype_output (int | float | bool, optional): The output type. Defaults to int.
        threshold (float, optional): The threshold to compare the array to. Defaults to 1e-6.
        output_array_type (ArrayTypes, optional): The output type. Defaults to "jax".

    Returns:
    """
    if isinstance(array, jnp.ndarray) or isinstance(array, np.ndarray):
        array = jnp.array(array)

    if isinstance(array, jnp.ndarray):
        array = jnp.abs(array) > threshold
    elif isinstance(array, np.ndarray):
        array = np.abs(array) > threshold
    else:
        raise ValueError("The array must be either a jax or numpy array.")
    array = array.astype(dtype_output)
    array = convert_array_type(array, output_array_type)
    return array


a2d = absolute_to_threshold
