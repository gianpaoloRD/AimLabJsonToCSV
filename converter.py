import json
from pathlib import Path
import pandas as pd

def load_json(path: Path) -> dict:
    # Open a JSON file from the given path (in read mode, UTF-8 encoded)
    with path.open("r", encoding="utf-8") as f:
        # Parse its contents into a Python dictionary
        return json.load(f)

def save_json(data: dict, path: Path):
    # Open the output file (write mode, UTF-8 encoding)
    with path.open("w", encoding="utf-8") as f:
        # Save the dictionary in JSON format with pretty indentation
        json.dump(data, f, indent=4, ensure_ascii=False)


def save_dataframe_as_csv(df: pd.DataFrame, path: Path):
    print(df)  # Print the DataFrame to the console for verification/debugging
    # Save the DataFrame to a CSV file without including row indexes
    df.to_csv(path, index=False, encoding="utf-8")
    print(f"✅ DataFrame saved as CSV to {path}")

def convert_structure(data: dict) -> dict:
    """
    Converts Unity-like nested structure into a simpler readable JSON.
    """
    # Get the first nested dictionary under "m_Data"
    root = data.get("m_Data", {})
    # Extract the actual list of entries (each one contains m_Value and m_Weight)
    inner = root.get("m_Data", [])
    # Extract "m_WeightMode" if it exists (sometimes found at root level)
    weight_mode = data.get("m_WeightMode", root.get("m_WeightMode", None))

    simplified = []  # This will hold the cleaned data entries

    # Loop through every item in the inner list
    for item in inner:
        val = item.get("m_Value", {})    # Get x/y values from "m_Value"
        weight = item.get("m_Weight", {})  # Get x/y values from "m_Weight"

        # Build a simpler dictionary with arrays for value and weight
        simplified.append({
            "value": [val.get("x"), val.get("y")],
            "weight": [weight.get("x"), weight.get("y")]
        })

    # Return a new dictionary with the simplified data and weight mode
    return {"data": simplified, "weight_mode": weight_mode}



def json_to_dataframe(data: dict) -> pd.DataFrame:
    # Prepare an empty list to hold row data
    records = []

    # Extract weight_mode to add it to every row
    weight_mode = data.get("weight_mode")

    # Enumerate over each data point in the "data" list
    for i, item in enumerate(data.get("data", [])):
        # Extract the x and y components from "value" and "weight"
        value_x, value_y = item["value"]
        weight_x, weight_y = item["weight"]

        # Build a single record (row)
        records.append({
            "index": i,
            "value_x": value_x,
            "value_y": value_y,
            "weight_x": weight_x,
            "weight_y": weight_y,
            "weight_mode": weight_mode
        })

    # Convert the list of dictionaries into a pandas DataFrame
    return pd.DataFrame(records)
