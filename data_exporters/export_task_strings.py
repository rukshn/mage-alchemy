import json

if "data_exporter" not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def export_data_to_file(data, **kwargs) -> None:
    task_strings = json.loads(data)
    filepath = "/home/src/Documents/repos/xml2xlsx/output/task.js"

    json_string = "\n".join(json.dumps(obj) for obj in task_strings)

    with open(filepath, "w") as file:
        file.write(json_string)
        file.close()
