import json
import csv
from pathlib import Path

# ------------------------------
# 1. Load JSON file
# ------------------------------
def load_json(path: Path) -> dict:
    """
    Opens and reads a JSON file from the given path.
    Returns the parsed JSON object as a Python dictionary.
    """
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

# ------------------------------
# 2. Helper: detect list of dictionaries
# ------------------------------
def is_list_of_dicts(value):
    """
    Checks whether the given value is a list in which every element is a dictionary.

    Returns:
        bool: True if the value is a non-empty list of dictionaries, otherwise False.

    Examples:
        >>> is_list_of_dicts([{"a": 1}, {"a": 2}])
        True
        >>> is_list_of_dicts([1, 2, 3])
        False
        >>> is_list_of_dicts([])
        False
    """

    # Ensure the input is a list
    if not isinstance(value, list):
        return False

    # An empty list is not considered a list of dicts
    if not value:
        return False

    # Check if every item in the list is a dictionary
    for item in value:
        if not isinstance(item, dict):
            return False

    # If we reach this point, all elements are dicts
    return True

# ------------------------------
# 3. Recursive flatten function
# ------------------------------
def flatten_obj(obj, parent_key="", sep="."):
    """
    Recursively flattens nested JSON/dictionary structures.
    Produces a flat dictionary where keys are full paths separated by dots.

    Example:
      {"a": {"b": 1}} → {"a.b": 1}
      {"x": [1,2,3]} → {"x": "1|2|3"}
      {"y": [{"z":1}, {"z":2}]} → {"y.0.z": 1, "y.1.z": 2}
    """
    items = {}  # Dictionary that will store flattened key-value pairs

    # Case 1: the object is a dictionary → iterate over its keys
    if isinstance(obj, dict):
        for k, v in obj.items():
            # Build the new key path (example: userSettings.audioSettings.masterVolume)
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            # Recursively flatten the value
            items.update(flatten_obj(v, new_key, sep=sep))

    # Case 2: the object is a list
    elif isinstance(obj, list):
        # Subcase: list of dictionaries → index each dictionary
        if is_list_of_dicts(obj):
            for i, v in enumerate(obj):
                new_key = f"{parent_key}{sep}{i}" if parent_key else str(i)
                items.update(flatten_obj(v, new_key, sep=sep))
        else:
            # Subcase: list of primitives (numbers, strings, etc.)
            # Join them with "|" so they fit in one CSV cell
            joined = "|".join(str(x) for x in obj)
            items[parent_key] = joined

    # Case 3: simple value (string, number, boolean, None)
    else:
        items[parent_key] = obj

    return items

# ------------------------------
# 4. Wrapper: flatten the entire JSON structure
# ------------------------------
def json_to_row(data: dict) -> dict:
    """
    Converts the full JSON structure into a single flattened row
    suitable for writing to a CSV file.
    """
    return flatten_obj(data)

# ------------------------------
# 5. Save as CSV
# ------------------------------
def write_csv(rows: list[dict], path: Path):
    """
    Writes one or more flattened JSON objects (rows) into a CSV file.

    Each dictionary in 'rows' represents one row in the CSV.
    All unique keys across those dictionaries become the CSV column headers.

    Args:
        rows (list[dict]): List of flattened JSON rows to write.
        path (Path): Destination file path for the CSV.

    Example:
        >>> data = [{"a": 1, "b": 2}, {"a": 3, "c": 4}]
        >>> write_csv(data, Path("output.csv"))
        # Output CSV will have columns: a, b, c
    """

    # --------------------------------------------
    # Step 1: Collect all unique column names
    # --------------------------------------------
    fieldnames = set()

    for row in rows:
        # Add all keys from each dictionary to the set
        fieldnames.update(row.keys())

    # Sort column names alphabetically for consistent output order
    fieldnames = sorted(fieldnames)

    # --------------------------------------------
    # Step 2: Open the target file for writing
    # --------------------------------------------
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # Write the header row (column names)
        writer.writeheader()

        # --------------------------------------------
        # Step 3: Write each flattened JSON row
        # --------------------------------------------
        for row in rows:
            writer.writerow(row)

    print(f"✅ CSV file successfully written to: {path}")

# ------------------------------
# 6. Main entry point
# ------------------------------
def main():
    """
    Main workflow:
      1. Load a JSON file
      2. Flatten it
      3. Save it as CSV
    """
    json_path = Path("Input/rob.json")  # Input file path
    csv_path = Path("aimlab_sample.csv")    # Output file path

    # Step 1: Load
    data = load_json(json_path)
    # Step 2: Flatten into a single row
    row = json_to_row(data)
    # Step 3: Save as CSV
    write_csv([row], csv_path)

    print(f"✅ CSV successfully saved to {csv_path}")

# ------------------------------
# 7. Run script
# ------------------------------
if __name__ == "__main__":
    main()
