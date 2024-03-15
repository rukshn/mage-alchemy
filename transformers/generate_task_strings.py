import numpy as np
import json
import pandas as pd

if "transformer" not in globals():
    from mage_ai.data_preparation.decorators import transformer
if "test" not in globals():
    from mage_ai.data_preparation.decorators import test


@transformer
def transform(data, *args, **kwargs):
    task_string_template = "content['{variableName}'] = getField(report, '{full_path}')"
    task_strings = {}
    missing_elements = pd.read_json(data["missing_elements"], orient="records")
    print(missing_elements)
    for index, row in missing_elements.iterrows():
        if row["nodeset_unparsed"] is np.nan:
            continue
        if row["nodeset_unparsed"] is None:
            continue
        unparsed = row["nodeset_unparsed"]
        split_unparsed = unparsed.split("/")
        parse_unparsed = ".".join(
            split_unparsed[1:-1]
        )  # remove the first and last element
        if parse_unparsed == "":
            full_path = row["name"]  # add the name to the end of the path
        else:
            full_path = (
                parse_unparsed + "." + row["name"]
            )  # add the name to the end of the path
        task_string = task_string_template.format(
            variableName=row["name"], full_path=full_path
        )
        task_strings[row["name"]] = task_string

    tast_string_list = list(task_strings.values())
    return json.dumps(tast_string_list)


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, "The output is undefined"
