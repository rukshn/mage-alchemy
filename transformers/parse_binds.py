if "transformer" not in globals():
    from mage_ai.data_preparation.decorators import transformer
if "test" not in globals():
    from mage_ai.data_preparation.decorators import test


from bs4 import BeautifulSoup
import json
import re
import pandas as pd

missing_elements = pd.DataFrame()
missing_elements = missing_elements._append(
    [
        {"type": "hidden", "name": "data"},
        {
            "type": "begin_group",
            "name": "inputs",
            "label": "NO_LABEL",
            "appearance": "field-list",
            "relevance": "./source='user'",
        },
        {
            "type": "hidden",
            "name": "data_load",
        },
        {
            "type": "integer",
            "name": "hidden_int",
            "relevance": "false()",
            "label": "NO_LABEL",
        },
        {
            "type": "hidden",
            "name": "source",
            "default": "user",
            "appearance": "hidden",
        },
        {"type": "hidden", "name": "source_id", "relevance": "hidden"},
        {
            "type": "begin_group",
            "name": "user",
            "appearance": "field-list",
            "label": "NO_LABEL",
        },
        {
            "type": "string",
            "name": "contract_id",
            "label": "NO_LABEL",
        },
        {
            "type": "string",
            "name": "facility_id",
            "label": "NO_LABEL",
        },
        {"type": "string", "name": "name", "label": "NO_LABEL"},
        {"type": "end_group", "name": "user"},
        {
            "type": "hidden",
            "name": "person_uuid",
        },
        {"type": "hidden", "name": "person_name"},
        {"type": "hidden", "name": "person_role"},
        {"type": "hidden", "name": "patient_uuid"},
        {
            "type": "begin_group",
            "appearence": "field-list",
            "name": "contact",
            "label": "NO_LABEL",
        },
        {"type": "string", "name": "_id", "label": "NO_LABEL"},
        {"type": "end_group", "name": "contact"},
        {
            "type": "calculate",
            "name": "source_id",
            "calculation": "../inputs/source_id",
        },
        {
            "type": "calculate",
            "name": "patient_uuid",
            "calculation": "../inputs/patient_uuid",
        },
    ],
    ignore_index=True,
)


def check_nodeset_in_df(nodeset, df):
    check_nodeset = df.loc[df["name"] == nodeset]
    if check_nodeset.empty:
        return False
    else:
        return True


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


def parse_missing_elements(instance, prelab_df):
    global missing_elements
    if "@case_id" in instance:
        pattern = re.compile(r"[,:><=+) ]")
        element = instance.split("]")[-1]
        split_element = pattern.split(element)
        element_key = split_element[0][1:].strip().replace("/", "_")
        if prelab_df is None:
            return

        find_prelab_element = prelab_df.loc[
            prelab_df["label"] == element_key, "nodeset"
        ]

        if find_prelab_element is not None:
            parsed_pre_lab_element = find_prelab_element
            unparsed_notdeset = prelab_df.loc[
                prelab_df["label"] == element_key, "nodeset_unparsed"
            ]

            if (
                len(
                    missing_elements.loc[
                        missing_elements["name"] == parsed_pre_lab_element.values[0],
                        "name",
                    ]
                )
                == 0
            ):
                missing_elements = missing_elements._append(
                    {
                        "type": "hidden",
                        "name": parsed_pre_lab_element.values[0],
                        "nodeset_unparsed": unparsed_notdeset.values[0],
                        "label": "NO_LABEL",
                    },
                    ignore_index=True,
                )

            parsed_element = re.sub(
                r"\b" + re.escape(element_key) + r"\b",
                "${" + find_prelab_element.values[0] + "}",
                element[1:],
            )
            # parsed_element = element[1:].replace(
            #     element_key, "${" + find_prelab_element.values[0] + "}"
            # )
            print(parsed_element)
            return parsed_element
        else:
            print("empty")


def parse_instance(instance, lookup_table_df, prelab_df):
    print(instance)
    if "@case_id" in instance:
        parsed_element = parse_missing_elements(instance, prelab_df)
        return parsed_element
    else:
        print("nothing found")
    # remove instance tags
    # remove the last paranthesis
    if instance.endswith(")"):
        instance = instance[:-1]

    try:
        out_statement = ""
        # drop text beteeen ) and [
        instance = re.sub(r"\)[^\]]*\[", ")[", instance)
        # extract text beteen paranthesis
        instance_items = re.search(r"\(\'(.*?)\'\)", instance)
        # extact instance name
        instance_name = instance_items.group(1).split(":")[1]
        # extract instance key value pairs
        instance_key_value = re.search(r"\[(.*?)\]", instance)
        instance_key = instance_key_value.group(1).split("=")[0].strip()
        instance_value = instance_key_value.group(1).split("=")[1].strip()
        # get the instance y param
        instance_y = instance.split("/")[-1].strip()

        # extract the sheet from the lookup table
        sheet_data = lookup_table_df.loc[lookup_table_df["sheet"] == instance_name]
        # extract the column from the sheet_data
        filter_sheet = sheet_data.loc[
            :, ["field: " + instance_key, "field: " + instance_y]
        ]

        # extract the value inside paranthesis in the instance_value
        instance_value_nodes = re.findall(r"\((.*?)\)", instance_value)
        # replace / with _
        instance_value_nodes_parsed = [
            "_".join(i[1:].split("/")) for i in instance_value_nodes
        ]

        # check if the instance_value_node is in the dataframe
        for index, instance_value_node in enumerate(instance_value_nodes):
            instance_value = instance_value.replace(
                instance_value_node, "${" + instance_value_nodes_parsed[index] + "}"
            )

        conditions = []
        results = []

        # iterate through the sheet_data and generate the conditions and results
        for index, row in sheet_data.iterrows():
            key_value = row["field: " + instance_key]

            # check if the key_value is a float
            # if it is convert it to int
            if type(key_value) == float:
                key_value = int(key_value)

            instance_logic = instance_key_value.group(1).replace(
                instance_key, "'" + str(key_value) + "'"
            )

            for index, instance_value_node in enumerate(instance_value_nodes):
                instance_logic = instance_logic.replace(
                    instance_value_node, "${" + instance_value_nodes_parsed[index] + "}"
                )
                conditions.append(instance_logic)

            results.append(row["field: " + instance_y])

        if len(conditions) > 1:
            nested_if_else_statement = generate_nested_if(
                conditions, results, default_result=""
            )
            out_statement = nested_if_else_statement
        if len(conditions) == 1:
            if_else_statement = generate_if_else(conditions[0], results[0], "")
            out_statement = if_else_statement

        return out_statement

    except Exception as e:
        print(f"WARNING: {e}")
        return instance


def generate_nested_if(conditions, results, default_result=""):
    """
    Generate a nested if statement in XLSForm format based on the provided conditions and results.

    Parameters:
    - conditions (list): List of conditions to check.
    - results (list): List of results corresponding to each condition.
    - default_result: Result to return if none of the conditions are true.

    Returns:
    - str: Generated XLSForm content.
    """
    if len(conditions) != len(results):
        raise ValueError("Number of conditions must be equal to the number of results.")

    xlsform_content = "if({condition}, '{true_result}', ".format(
        condition=conditions[0], true_result=results[0]
    )

    for i, (condition, result) in enumerate(zip(conditions[1:], results[1:])):
        xlsform_content += f"if({condition}, '{result}', "

    xlsform_content += f"'{default_result}'"

    # Add closing parentheses for each nested if
    for _ in range(len(conditions)):
        xlsform_content += ")"

    return xlsform_content


@transformer
def transform(data, data_2, data_3, *args, **kwargs):
    print(data)
    json_data = None
    prelab_df = data
    json_data = data_3["xml_structure"]
    lookup_table_df = pd.read_json(data_2["lookup_table"], orient="records")
    df = pd.read_json(data_2["dataframe"], orient="records")

    if json_data is None:
        return None

    soup = json.loads(json_data)
    soup = BeautifulSoup(soup, "xml")
    binds = soup.find_all("bind")
    for bind in binds:
        nodeset = bind.get("nodeset")[1:]
        nodeset_unparsed = nodeset
        nodeset = "_".join(nodeset.split("/"))
        # print(nodeset)
        df.loc[df["name"] == nodeset, "nodeset"] = nodeset
        df.loc[df["name"] == nodeset, "nodeset_unparsed"] = nodeset_unparsed
        df.loc[df["name"] == nodeset, "required"] = bind.get("required")
        bind_relevant = bind.get("relevant")

        # map relevant
        if bind_relevant is not None:
            while bind_relevant.__contains__("casedb"):
                bind_relevant_re = re.search(r"instance(.*?)(?:,|\))", bind_relevant)
                if bind_relevant_re is not None:
                    pattern = re.compile(r"instance\('.+?'\)/.+?\[")
                    matches = pattern.findall(bind_relevant)
                    split_relevant = matches[0]
                    replace_instance_with_logic = parse_instance(
                        bind_relevant.split("[")[1], lookup_table_df, prelab_df
                    )
                    bind_relevant = bind_relevant.replace(
                        split_relevant + bind_relevant.split("[")[1],
                        replace_instance_with_logic,
                    )
            extract_instance_tags = bind_relevant.split(",")
            for instance in extract_instance_tags:
                instance_re = re.search(r"\binstance(.*?)(?:,|\))", instance)
                if instance_re is not None:
                    if instance.endswith(")"):
                        bind_relevant = bind_relevant.replace(
                            instance, replace_instance_with_logic + ")"
                        )
                    else:
                        bind_relevant = bind_relevant.replace(
                            instance, replace_instance_with_logic
                        )
                    if "commcare" in instance:
                        print(f"Possible commcare header: {instance}")
                else:
                    continue

            bind_relevant_regex = re.findall(r"\/[^\s=]+", bind_relevant)
            bind_relevant_regex = sorted(bind_relevant_regex, key=len, reverse=True)
            for reg in bind_relevant_regex:
                reg = reg.strip()
                if reg.endswith(",") or reg.endswith(")"):
                    reg_filter = reg[1:-1]
                    reg_to_name = "_".join(reg_filter.split("/"))
                    if check_nodeset_in_df(reg_to_name, df):
                        bind_relevant = bind_relevant.replace(
                            reg, "${" + reg_to_name + "}" + reg[-1]
                        )

                else:
                    reg_filter = reg[1:]
                    reg_to_name = "_".join(reg_filter.split("/"))
                    if check_nodeset_in_df(reg_to_name, df):
                        bind_relevant = bind_relevant.replace(
                            reg, "${" + reg_to_name + "}"
                        )

            df.loc[df["name"] == nodeset, "relevance"] = bind_relevant

        # map constraints
        bind_constratint = bind.get("constraint")
        if bind_constratint is not None:
            bind_constratint_regex = re.findall(r"\/[^\s=]+", bind_constratint)
            bind_constratint_regex = sorted(
                bind_constratint_regex, key=len, reverse=True
            )
            for reg in bind_constratint_regex:
                reg = reg.strip()
                if reg.endswith(",") or reg.endswith(")"):
                    reg_filter = reg[1:-1]
                    reg_to_name = "_".join(reg_filter.split("/"))

                    if check_nodeset_in_df(reg_to_name, df):
                        bind_constratint = bind_constratint.replace(
                            reg, "${" + reg_to_name + "}" + reg[-1]
                        )

                else:
                    reg_filter = reg[1:]
                    reg_to_name = "_".join(reg_filter.split("/"))
                    if check_nodeset_in_df(reg_to_name, df):
                        bind_constratint = bind_constratint.replace(
                            reg, "${" + reg_to_name + "}"
                        )

            df.loc[df["name"] == nodeset, "constraint"] = bind_constratint

        # map calculations
        bind_calculate = bind.get("calculate")
        if bind_calculate is not None:
            if "weight_estimated" in bind_calculate:
                temp = bind_calculate
            while bind_calculate.__contains__("casedb"):
                bind_calculate_re = re.search(r"instance(.*?)(?:,|\))", bind_calculate)
                if bind_calculate_re is not None:
                    pattern = re.compile(r"instance\('.+?'\)/.+?\[")
                    matches = pattern.findall(bind_calculate)
                    split_calculate = matches[0]
                    replace_instance_with_logic = parse_instance(
                        bind_calculate.split("[")[1], lookup_table_df, prelab_df
                    )
                    bind_calculate = bind_calculate.replace(
                        split_calculate + bind_calculate.split("[")[1],
                        replace_instance_with_logic,
                    )
            extract_instance_tags = bind_calculate.split(",")
            for instance in extract_instance_tags:
                instance_re = re.search(r"\binstance(.*?)(?:,|\))", instance)
                if instance_re is not None:
                    replace_instance_with_logic = parse_instance(
                        instance, lookup_table_df, prelab_df
                    )

                    if instance.endswith(")"):
                        bind_calculate = bind_calculate.replace(
                            instance, replace_instance_with_logic + ")"
                        )
                    else:
                        bind_calculate = bind_calculate.replace(
                            instance, replace_instance_with_logic
                        )
                    if "commcare" in instance:
                        print(f"Possible commcare header: {instance}")
                else:
                    continue

            bind_calculate_regex = re.findall(r"\/[^\s=]+", bind_calculate)
            bind_calculate_regex = sorted(bind_calculate_regex, key=len, reverse=True)
            for reg in bind_calculate_regex:
                reg = reg.strip()
                if reg.endswith(",") or reg.endswith(")"):
                    reg_filter = reg[1:-1]
                    reg_to_name = "_".join(reg_filter.split("/"))

                    if check_nodeset_in_df(reg_to_name, df):
                        bind_calculate = bind_calculate.replace(
                            reg, "${" + reg_to_name + "}" + reg[-1]
                        )
                else:
                    reg_filter = reg[1:]
                    reg_to_name = "_".join(reg_filter.split("/"))
                    if check_nodeset_in_df(reg_to_name, df):
                        bind_calculate = bind_calculate.replace(
                            reg, "${" + reg_to_name + "}"
                        )

            df.loc[df["name"] == nodeset, "calculation"] = bind_calculate

        # map constraintMsg
        constraint_message = bind.get("jr:constraintMsg")
        if constraint_message is not None:
            constraint_message = constraint_message.split("'")[1]
            constraint_labels = get_label_value(constraint_message, soup)
            if constraint_labels is not None:
                for lang, label in constraint_labels.items():
                    if label is not None:
                        label = label.strip()
                    df.loc[df["name"] == nodeset, "constraint_message::" + lang] = label

        # map requiredMsg
        required_message = bind.get("jr:requiredMsg")
        if required_message is not None:
            required_message = required_message.split("'")[1]
            required_message_labels = get_label_value(required_message, soup)
            for lang, label in required_message_labels.items():
                if label is not None:
                    label = label.strip()
                df.loc[df["name"] == nodeset, "required_message::" + lang] = label

        # map types
        # currently this form has only these types, however there are more odk type
        # this has to mapped with more xml files when available
        bind_type = bind.get("type")

        bind_read_only = bind.get("readonly")

        if bind_read_only == "true()":
            df.loc[df["name"] == nodeset, "type"] = "note"
        elif bind_type is not None and "string" in bind_type:
            df.loc[df["name"] == nodeset, "type"] = "string"
        elif bind_type is not None and "int" in bind_type:
            df.loc[df["name"] == nodeset, "type"] = "integer"
        elif bind_type is not None and "double" in bind_type:
            df.loc[df["name"] == nodeset, "type"] = "decimal"
        elif bind_type is not None and "dateTime" in bind_type:
            df.loc[df["name"] == nodeset, "type"] = "dateTime"
        elif bind_type is not None and "date" in bind_type:
            df.loc[df["name"] == nodeset, "type"] = "date"
        elif bind_type is not None and "geopoint" in bind_type:
            df.loc[df["name"] == nodeset, "type"] = "geopoint"
        elif bind_type is not None and "geotrace" in bind_type:
            df.loc[df["name"] == nodeset, "type"] = "geotrace"
    if kwargs["mode"] == "posttest":
        missing_elements_json = missing_elements.to_json(orient="records")
        dataframe = df.to_json(orient="records")
        return {"dataframe": dataframe, "missing_elements": missing_elements_json}
    else:
        return df


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, "The output is undefined"
