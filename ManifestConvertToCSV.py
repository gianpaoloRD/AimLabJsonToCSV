import json
import csv
from pathlib import Path

BASE_DIR = Path("Data")  # Root folder (same as Omnisense script)
TARGET_JSON_NAME = "analyticsPayload.json"  # Change to your real analytics JSON filename
OUTPUT_DIR = Path("output")  # Output folder for the stats CSVs


def build_output_name(json_path: Path, base_dir: Path) -> Path:
    # Example:
    #   base_dir = Data
    #   json_path = Data/Players/P001/Session 1/analyticsPayload.json
    #   rel parts = ("Players", "P001", "Session 1", "analyticsPayload.json")
    #   CSV name = DataPlayersP001Session1_stats.csv

    rel = json_path.relative_to(base_dir)
    components = [base_dir.name] + list(rel.parts[:-1])
    flat_name = "".join(part.replace(" ", "") for part in components)
    return OUTPUT_DIR / f"{flat_name}_stats.csv"


def convert_single_file(json_path: Path, csv_path: Path):
    data = load_json(json_path)
    row = json_to_row(data)
    write_csv([row], csv_path)
    print(f"✅ Converted {json_path} → {csv_path}")


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
    """
    if not isinstance(value, list):
        return False
    if not value:
        return False
    for item in value:
        if not isinstance(item, dict):
            return False
    return True


# ------------------------------
# 3. Recursive flatten function
# ------------------------------
def flatten_obj(obj, parent_key="", sep="."):
    """
    Recursively flattens nested JSON/dictionary structures.
    Produces a flat dictionary where keys are full paths separated by dots.
    """
    items = {}

    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            items.update(flatten_obj(v, new_key, sep=sep))

    elif isinstance(obj, list):
        if is_list_of_dicts(obj):
            for i, v in enumerate(obj):
                new_key = f"{parent_key}{sep}{i}" if parent_key else str(i)
                items.update(flatten_obj(v, new_key, sep=sep))
        else:
            joined = "|".join(str(x) for x in obj)
            items[parent_key] = joined

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
    """
    fieldnames = set()
    for row in rows:
        fieldnames.update(row.keys())
    fieldnames = sorted(fieldnames)

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print(f"✅ CSV file successfully written to: {path}")


# ------------------------------
# 6. Main entry point
# ------------------------------
def main():
    if not BASE_DIR.exists():
        print(f"❌ Base directory not found: {BASE_DIR}")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    matches = list(BASE_DIR.rglob(TARGET_JSON_NAME))
    if not matches:
        print(f"⚠️ No files named '{TARGET_JSON_NAME}' found under {BASE_DIR}")
        return

    print(f"🔍 Found {len(matches)} file(s) named '{TARGET_JSON_NAME}'")

    for json_path in matches:
        out_csv = build_output_name(json_path, BASE_DIR)
        convert_single_file(json_path, out_csv)

    print("🎉 Done converting all analytics stats files.")


if __name__ == "__main__":
    main()
