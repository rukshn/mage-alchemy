if "condition" not in globals():
    from mage_ai.data_preparation.decorators import condition


@condition
def evaluate_condition(*args, **kwargs) -> bool:
    if kwargs["mode"] == "posttest":
        return True
    else:
        return False
