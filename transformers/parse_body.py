if "transformer" not in globals():
    from mage_ai.data_preparation.decorators import transformer
if "test" not in globals():
    from mage_ai.data_preparation.decorators import test

import pandas as pd
import json
from bs4 import BeautifulSoup
import re


def get_label_value(text_id, soup):
    translations = soup.find("itext").find_all("translation")
    output = {}
    for translation in translations:
        translation_lang = translation.get("lang")
        labels = translation.find("text", id=text_id)
        if labels is None:
            text_value = None

        elif labels.find("value", form="markdown") is not None:
            text_value = labels.find("value", form="markdown").get_text()
        else:
            text_value = labels.find("value").get_text()
        output[translation_lang] = text_value
    return output


def extract_lookup_table_data(sheet_name, lookup_table_df):
    sheet_data = lookup_table_df.loc[lookup_table_df["sheet"] == sheet_name]
    return sheet_data


@transformer
def transform(data, data_2, data_3, *args, **kwargs):
    json_data = None
    # df = pd.read_json(data_2["dataframe"], orient="records")
    df = pd.read_json(data["dataframe"], orient="records")
    lookup_table = pd.read_json(data_2["lookup_table"], orient="records")
    json_data = data_3["xml_structure"]

    if json_data is None:
        return None

    df_choice = pd.DataFrame(
        columns=["list_name", "name", "value", "media", "read_only"]
    )
    form_structure = json.loads(json_data)
    soup = BeautifulSoup(form_structure, "xml")
    body = soup.find("h:body")

    for tag in body.find_all(recursive=True):
        tag_ref = tag.get("ref")
        tag_name = tag.name
        tag_appearance = tag.get("appearance")
        tag_ref_to_name = None
        tag_name_regex = None
        df_name = None

        if tag_ref is None:
            continue

        tag_ref_regex = re.findall(r"\/[^\s=':)]+", tag_ref)
        for reg in tag_ref_regex:
            tag_ref_to_name = "_".join(reg.split("/")[1:])

        if tag_name == "select1":
            df.loc[df["name"] == tag_ref_to_name, "type"] = (
                "select_one " + tag_ref_to_name
            )

            # parse itemset tags if available
            itemset = tag.find("itemset")
            if itemset is not None:
                itemset_reference = itemset.get("nodeset")
                # extract the instance name within the nodeset

            for child in tag.find_all("item"):
                child_label = child.find("label").get("ref")
                child_label = child_label.split("'")[1]
                df_element_name = child_label.split("/")[-1].split(":")[0]
                label_values = get_label_value(child_label, soup)

                choice = {}
                for lang, label in label_values.items():
                    choice["label::" + lang] = label

                choice["list_name"] = tag_ref_to_name
                choice["name"] = df_element_name
                df_choice = df_choice._append(choice, ignore_index=True)

        elif tag_name == "select":
            df.loc[df["name"] == tag_ref_to_name, "type"] = (
                "select_multiple " + tag_ref_to_name
            )

            # parse itemset tags if available
            itemset = tag.find("itemset")
            if itemset is not None:
                itemset_reference = itemset.get("nodeset")
                # extract the instance name within the nodeset
                instance = re.search(r"'(.*?)'", itemset_reference)
                instance = instance.group(1)
                lookup_data = extract_lookup_table_data(instance, lookup_table)
                fields = re.search(r"\[(.*?)\]", itemset_reference)
                fields = fields.group(1).split(" ")

                filtered_field_dataframe = pd.DataFrame()
                refined_fields = ["field: value", "field: label 1"]
                for field in fields:
                    if field.__contains__("/"):
                        field = field.split("/")[-1]

                    field = field.replace("/", "_")
                    refined_fields.append("field: " + field)

                valid_columns = list(
                    set(refined_fields).intersection(lookup_data.columns)
                )
                filtered_field_dataframe = lookup_data[valid_columns]
                filtered_field_dataframe = filtered_field_dataframe.copy()
                filtered_field_dataframe.loc[:, "list_name"] = tag_ref_to_name

                filtered_field_dataframe_columns = (
                    filtered_field_dataframe.columns.tolist()
                )

                for column in filtered_field_dataframe_columns:
                    column = column.strip()
                    if ":" in column:
                        column_post = column.split(":")[1]
                        column_post = column_post.strip()
                        filtered_field_dataframe = filtered_field_dataframe.rename(
                            columns={column: column_post}
                        )

                filtered_field_dataframe = filtered_field_dataframe.rename(
                    columns={"label 1": "label"}
                )

                df_choice = pd.concat(
                    [df_choice, filtered_field_dataframe], ignore_index=True
                )
                # for data in lookup_data:
                #     print(data)

            for child in tag.find_all("item"):
                child_label = child.find("label").get("ref")
                child_label = child_label.split("'")[1]
                df_element_name = child_label.split("/")[-1].split(":")[0]
                label_value = get_label_value(child_label, soup)

                choice = {}

                for lang, label in label_value.items():
                    choice["label::" + lang] = label

                choice["list_name"] = tag_ref_to_name
                choice["name"] = df_element_name

                # value = child.find("value").get_text()
                df_choice = df_choice._append(choice, ignore_index=True)
            # df.loc[df["name"] == tag_ref_to_name, "type"] = odk_type

        if tag_appearance == "field-list":
            df_name = tag_ref.split("/")[-1]
            df.loc[df["name"] == df_name, "appearance"] = "field-list"

        elif tag_appearance is not None:
            df.loc[df["name"] == tag_ref_to_name, "appearance"] = tag_appearance

    df_to_json = df.to_json(orient="records")
    df_choice_to_json = df_choice.to_json(orient="records")
    return {"dataframe": df_to_json, "dataframe_choices": df_choice_to_json}


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, "The output is undefined"
