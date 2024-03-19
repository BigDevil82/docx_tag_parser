import json
import os


class DataContextManager:
    def __init__(self, json_data) -> None:
        if os.path.exists(json_data):
            with open(json_data, "r", encoding="utf-8") as f:
                json_str = f.read()
                self.json = json.loads(json_str)
        else:
            self.json = json.loads(json_data)

        self.data_context = self.json

    def get_json_value(self, key, data_context=None):
        """
        Retrieve corresponding value for the given key from the JSON data

        Args:
            data_context (dict, optional): The data context to search for the key.

        Returns:
            str: The corresponding value from the JSON data.
        """

        if data_context is None:
            data_context = self.data_context

        if isinstance(data_context, list):
            return ""

        val = data_context.get(key, None)
        # try to get from the "Sharing" part
        val = val if val is not None else self.json["Sharing"].get(key, None)

        return val if val is not None else ""
