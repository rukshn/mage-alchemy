import pandas as pd

if "data_exporter" not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def export_data_to_file(data, data_2, data_3, **kwargs) -> None:
    filepath = data_2["posttest_output_file"]

    df_choice = pd.read_json(data_3["dataframe_choices"], orient="records")
    df = pd.read_json(data["dataframe"], orient="records")
    df_settings = pd.read_json(data["settings"], orient="records")

    with pd.ExcelWriter(filepath) as writer:
        df.to_excel(writer, sheet_name="survey")
        df_choice.to_excel(writer, sheet_name="choices")
        df_settings.to_excel(writer, sheet_name="settings")
        writer.save()
        writer.close()
