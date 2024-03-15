if "transformer" not in globals():
    from mage_ai.data_preparation.decorators import transformer
if "test" not in globals():
    from mage_ai.data_preparation.decorators import test


from bs4 import BeautifulSoup
import json
import pandas as pd
import re


@transformer
def transform(data, data_2, *args, **kwargs):
    df = pd.read_json(data["dataframe"], orient="records")
    json_form = data_2["xml_structure"]

    form_structure = json.loads(json_form)
    soup = BeautifulSoup(form_structure, "xml")

    df["has_label"] = False
    translations = soup.find("itext").find_all("translation")

    for translation in translations:
        translation_lang = translation.get("lang")
        column_name = "label" + "::" + translation_lang

        for text in translation.find_all("text"):
            if ":jr:constraintMsg" in text.get("id"):
                continue
            text_content = text.contents
            text_id = text.get("id")
            text_id_regex = re.findall(r"\/[^\s=':)]+", text_id)
            text_id_to_name = "_".join(text_id_regex[0].split("/")[1:])

            text_value = text.find("value", form="markdown")
            if text_value is not None:
                output_tag = text_value.find_all("output")
                if output_tag is not None and len(output_tag) > 0:
                    for output in output_tag:
                        output_tag_value = output.get("value")
                        output_value_to_name = "_".join(output_tag_value.split("/")[1:])
                        output.replace_with("${" + output_value_to_name + "}")
                df.loc[df["name"] == text_id_to_name, column_name] = (
                    text_value.get_text().strip()
                )
                df.loc[df["name"] == text_id_to_name, "has_label"] = True
            else:
                text_value = text.find("value")
                output_tag = text_value.find_all("output")
                if output_tag is not None and len(output_tag) > 0:
                    for output in output_tag:
                        output_tag_value = output.get("value")
                        output_value_to_name = "_".join(output_tag_value.split("/")[1:])
                        output.replace_with("${" + output_value_to_name + "}")
                df.loc[df["name"] == text_id_to_name, column_name] = (
                    text_value.get_text().strip()
                )
                df.loc[df["name"] == text_id_to_name, "has_label"] = True

    return df


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, "The output is undefined"
