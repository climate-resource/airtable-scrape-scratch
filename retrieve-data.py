"""
Retrieve Airtable data
"""

import json
import os
from pathlib import Path
from typing import Annotated

import requests
import typer
from dotenv import load_dotenv
from pyairtable import Api


def main(
    base_id: Annotated[
        str,
        typer.Option(
            help="""Base ID of the Airtable data to retrieve

This base ID can be retrieved by looking at the Airtable URL,
it's the bit after airtable.com.

For more information, see https://support.airtable.com/v1/docs/finding-airtable-ids"""
        ),
    ] = "appYl7TnOKv7KcneR",
    out_path=Annotated[
        Path, typer.Option(help="""Path in which to write the retrieved tables""")
    ],
):
    """
    Retrieve the data
    """
    load_dotenv()

    ACCESS_TOKEN = os.environ["AIRTABLE_ACCESS_TOKEN"]
    out_path = Path(out_path)
    out_path.mkdir(parents=True, exist_ok=True)

    api = Api(ACCESS_TOKEN)

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
        with open(out_path / f"{name}.json", "w") as fh:
            json.dump(table_rows, fh, indent=2, sort_keys=True)

        column_info = {}
        for ti in table_info["fields"]:
            try:
                description = ti["description"]
            except KeyError:
                description = "not provided"

            column_info[ti["name"]] = description

        with open(out_path / f"{name}-columns.json", "w") as fh:
            json.dump(column_info, fh, indent=2, sort_keys=True)


if __name__ == "__main__":
    typer.run(main)
