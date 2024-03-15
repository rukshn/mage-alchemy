import pandas as pd

if "data_loader" not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if "test" not in globals():
    from mage_ai.data_preparation.decorators import test


# data -> dataframe from the export
@data_loader
def load_data_from_file(data, *args, **kwargs):
    dataFrame = data
    dataFrame = dataFrame.drop(index=[0, len(dataFrame) - 1]).reset_index(drop=True)
    return dataFrame


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, "The output is undefined"
