if "transformer" not in globals():
    from mage_ai.data_preparation.decorators import transformer
if "test" not in globals():
    from mage_ai.data_preparation.decorators import test

import pandas as pd


@transformer
def transform(data, data_2, *args, **kwargs):
    df = data
    # change type of the dataframe to calculate if the label name has not changed
    exclusion_condition = df["type"].str.contains("begin_group") | df[
        "type"
    ].str.contains("end_group")
    inclusion_condition = df["has_label"] == False
    df.loc[
        ~exclusion_condition & inclusion_condition,
        "type",
    ] = "calculate"

    form_title = data_2["form_title"]
    form_id = data_2["form_id"]
    form_version = data_2["version"]
    default_language = data_2["default_language"]

    df = df.drop(index=[0, len(df) - 1]).reset_index(drop=True)

    setting_df = pd.DataFrame()
    setting_df._append(
        {
            "form_title": form_title,
            "form_id": form_id,
            "version": form_version,
            "default_language": default_language,
            "style": "pages",
        },
        ignore_index=True,
    )

    df.loc[df["type"] == "end_group", "label"] = None
    df.loc[df["type"] == "end_group", "appearance"] = None
    df.loc[df["type"] == "end_group", "relevance"] = None
    df["type"] = df["type"].fillna("note")

    setting_df_to_json = setting_df.to_json(orient="records")
    df_to_json = df.to_json(orient="records")

    return {"dataframe": df_to_json, "settings": setting_df_to_json}


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, "The output is undefined"
