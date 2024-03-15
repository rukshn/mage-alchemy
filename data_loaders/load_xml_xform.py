from mage_ai.io.file import FileIO
from bs4 import BeautifulSoup
import json

if "data_loader" not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if "test" not in globals():
    from mage_ai.data_preparation.decorators import test

soup = None


@data_loader
def load_data_from_file(*args, **kwargs):
    xml = None

    inputFile = kwargs["pretestXML"]

    with open(inputFile, "r") as file:
        xml = file.read()

    if xml is not None:
        soup = BeautifulSoup(xml, "xml")
        json_data = json.dumps(soup.prettify(), indent=2)

        return {"status": "xml loaded", "xml_structure": json_data}
    else:
        return None


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, "The output is undefined"
