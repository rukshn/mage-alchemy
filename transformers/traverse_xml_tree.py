if "transformer" not in globals():
    from mage_ai.data_preparation.decorators import transformer
if "test" not in globals():
    from mage_ai.data_preparation.decorators import test

import pandas as pd
from bs4 import BeautifulSoup
import json

df = pd.DataFrame()
globe_parents = []


def traverse(t, current_path=None):
    global df
    global globe_parents
    parents = []

    if current_path is None:
        current_path = [t.name]

    for tag in t.find_all(recursive=False):
        if not tag.find():
            node_type = None
            # print(" -> ".join(current_path + [tag.name]))
            # print(tag.name)
            if current_path[-1] not in parents:
                if len(parents) > 0:
                    node_name = parents[-1], "_", current_path[-1]
                else:
                    node_name = "data_" + current_path[-1]

                parents.append(current_path[-1])
                globe_parents.append(current_path[-1])
                node_type = "begin_group"
                df = df._append(
                    {
                        "type": node_type,
                        "name": node_name,
                        "label": tag.name,
                        "hint": "",
                        "constraint": "",
                        "constraint_message": "",
                        "required": "",
                        "default": "",
                        "relevance": "",
                        "calculation": "",
                        "choice_filter": "",
                        "appearance": "field-list",
                        "media": "",
                        "read_only": "",
                        "node_set": "",
                    },
                    ignore_index=True,
                )

            df = df._append(
                {
                    "type": None,
                    "name": "_".join(current_path + [tag.name]).replace(
                        "[document]_", ""
                    ),
                    "label": tag.name,
                    "hint": "",
                    "constraint": "",
                    "constraint_message": "",
                    "required": "",
                    "default": "",
                    "relevance": "",
                    "calculation": "",
                    "choice_filter": "",
                    "appearance": "",
                    "media": "",
                    "read_only": "",
                    "node_set": "",
                },
                ignore_index=True,
            )

            if (tag == t.find_all(recursive=False)[-1]) and (
                current_path[-1] in parents
            ):
                # print("end_group", current_path[-1])
                parents.remove(current_path[-1])
                globe_parents.remove(current_path[-1])
        else:
            traverse(tag, current_path + [tag.name])
            df = df._append(
                {
                    "type": "end_group",
                    "name": "data_" + tag.name,
                    "label": tag.name,
                    "hint": "",
                    "constraint": "",
                    "constraint_message": "",
                    "required": "",
                    "default": "",
                    "relevance": "",
                    "calculation": "",
                    "choice_filter": "",
                    "appearance": "",
                    "media": "",
                    "read_only": "",
                    "node_set": "",
                },
                ignore_index=True,
            )


@transformer
def transform(data, data_2, *args, **kwargs):
    global df

    lookup_table_df = pd.read_json(data_2["lookup_table"], orient="records")

    form_structure = data["form_structure"]
    form_structure = json.loads(form_structure)
    form_structure = BeautifulSoup(form_structure, "xml")

    traverse(form_structure)
    lookup_table_to_json = lookup_table_df.to_json(orient="records")
    df_to_json = df.to_json(orient="records")
    print(df_to_json)
    return {
        "lookup_table": lookup_table_to_json,
        "dataframe": df_to_json,
    }


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, "The output is undefined"
