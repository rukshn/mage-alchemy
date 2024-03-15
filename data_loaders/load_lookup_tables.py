import pandas as pd 

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

@data_loader
def load_data_from_file(*args, **kwargs):

    lookup_table_df = pd.DataFrame()
    lookup_table_path = kwargs["lookupTablePath"]
    
    lookup_excel = pd.read_excel(lookup_table_path, sheet_name=None)
    data_frame_with_sheet_name = []

    for sheet, dataframe in lookup_excel.items():
        dataframe["sheet"] = sheet
        data_frame_with_sheet_name.append(dataframe)

    df = pd.concat(data_frame_with_sheet_name, ignore_index=True)
    df_json = df.to_json(orient="records")
    return {
        "lookup_table": df_json
    }


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
