"""
Retrieve Airtable data
"""

import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from pyairtable import Api


def main():
    """
    Retrieve the data
    """
    load_dotenv()

    ACCESS_TOKEN = os.environ["AIRTABLE_ACCESS_TOKEN"]
    OUT_PATH = Path("retrieved-airtable-data")
    OUT_PATH.mkdir(parents=True, exist_ok=True)

    api = Api(ACCESS_TOKEN)

    # I had to copy the IPO's table to make one that I could access.
    # Not the end of the world and not sure how to make the IPO one more open.
    base_id = "appYl7TnOKv7KcneR"
    response_tables = requests.get(
        f"https://api.airtable.com/v0/meta/bases/{base_id}/tables",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
        timeout=30,
    )
    response_tables_json = response_tables.json()

    for table_info in response_tables_json["tables"]:
        name = table_info["name"]
        print(f"Retrieving the {name!r} table")
        table = api.table(base_id, table_info["id"])
        table_records = table.all()

        table_rows = [row["fields"] for row in table_records]
        with open(OUT_PATH / f"{name}.json", "w") as fh:
            json.dump(table_rows, fh, indent=2, sort_keys=True)

        column_info = {}
        for ti in table_info["fields"]:
            try:
                description = ti["description"]
            except KeyError:
                description = "not provided"

            column_info[ti["name"]] = description

        with open(OUT_PATH / f"{name}-columns.json", "w") as fh:
            json.dump(column_info, fh, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
