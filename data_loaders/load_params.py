if "data_loader" not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if "test" not in globals():
    from mage_ai.data_preparation.decorators import test


from datetime import date


@data_loader
def load_data(*args, **kwargs):
    """
    Template code for loading data from any source.

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    # Specify your data loading logic here

    if "version" not in kwargs:
        version = date.today().strftime("%d%m%Y")
    else:
        version = kwargs["version"]

    if "formTitle" not in kwargs:
        return None  # or raise an error

    if "formId" not in kwargs:
        return None

    if "pretestOutputFile" not in kwargs:
        pretest_output_file = version + "_pretest.xlsx"
    else:
        pretest_output_file = kwargs["pretestOutputFile"]

    if "posttestOutputFile" not in kwargs:
        posttest_output_file = version + "_posttest.xlsx"
    else:
        posttest_output_file = kwargs["posttestOutputFile"]

    if "defaultLanguge" not in kwargs:
        default_language = "en"
    else:
        default_language = kwargs["defaultLanguage"]

    return {
        "form_title": kwargs["formTitle"],
        "form_id": kwargs["formId"],
        "version": version,
        "pretest_output_file": pretest_output_file,
        "posttest_output_file": posttest_output_file,
        "default_language": default_language,
    }


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, "The output is undefined"
