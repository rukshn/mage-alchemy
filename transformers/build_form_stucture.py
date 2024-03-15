if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

import json 
from bs4 import BeautifulSoup

@transformer
def transform(data, *args, **kwargs):
    """
    Template code for a transformer block.

    Add more parameters to this function if this block has multiple parent blocks.
    There should be one parameter for each output variable from each parent block.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    # Specify your transformation logic here

    json_data = data["xml_structure"]
    form_structure = json.loads(json_data)
    form_structure = BeautifulSoup(form_structure, "xml")
    form_structure = form_structure.find("instance").find("data")
    
    json_form_structure = json.dumps(form_structure.prettify(), indent = 2)
    print(json_form_structure)
    if form_structure is not None:
        return {
            "form_structure": json_form_structure
        }
        
    else:
        return None

@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
