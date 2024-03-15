from mage_ai.io.file import FileIO
from pandas import DataFrame

if "data_exporter" not in globals():
    from mage_ai.data_preparation.decorators import data_exporter

import pandas as pd


@data_exporter
# data -> refine_dataframe
# datA_2 -> parse_body
# data_3 -> load_params
def export_data_to_file(data, data_2, data_3, **kwargs) -> None:
    filepath = data_3["pretest_output_file"]

    df_choice = pd.read_json(data_2["dataframe_choices"], orient="records")
    df = pd.read_json(data["dataframe"], orient="records")
    df_settings = pd.read_json(data["settings"], orient="records")

    with pd.ExcelWriter(filepath) as writer:
        df.to_excel(writer, sheet_name="survey")
        df_choice.to_excel(writer, sheet_name="choices")
        df_settings.to_excel(writer, sheet_name="settings")

        writer.save()
        writer.close()

    return df
