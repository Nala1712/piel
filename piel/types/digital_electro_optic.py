from pydantic import field_validator
import pandas as pd
from .core import PielBaseModel


class PhaseBitDataFrameModel(PielBaseModel):
    """
    A Pydantic model to validate that a DataFrame contains the required columns: 'bit' and 'phase'.
    """

    dataframe: pd.DataFrame

    @field_validator("dataframe")
    def validate_dataframe(cls, dataframe: pd.DataFrame):
        """
        Validate that the DataFrame contains 'bit' and 'phase' columns.
        """
        required_columns = {"bits", "phase"}
        if not required_columns.issubset(dataframe.columns):
            missing_columns = required_columns - set(dataframe.columns)
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

        return dataframe

    class Config:
        arbitrary_types_allowed = True


class PhaseBitDataFrame(pd.DataFrame):
    """
    A custom DataFrame class that ensures the DataFrame has 'bit' and 'phase' columns.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Validate using the pydantic model
        PhaseBitDataFrameModel(dataframe=self)
        # No need to reassign self; validation is already performed alization
        self.validate_columns(self)


PhaseMapType = PhaseBitDataFrame
