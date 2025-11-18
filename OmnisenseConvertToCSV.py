from pathlib import Path
from converter import (
    load_json,
    convert_structure,
    save_json,
    json_to_dataframe,
    save_dataframe_as_csv,
)

# ====== CONFIGURABLE SETTINGS ======
BASE_DIR = Path("Data")  # root folder where Players/ live
TARGET_JSON_NAME = "OmniSenseSettings.json"  # filename to search for
OUTPUT_DIR = Path("output")  # where all CSVs will be written
# ===================================


def build_output_name(json_path: Path, base_dir: Path) -> Path:
    # Example:
    #   base_dir = Data
    #   json_path = Data/Players/P001/Session 1/OmniSenseSettingsLOGI.json
    #   rel parts = ("Players", "P001", "Session 1", "OmniSenseSettingsLOGI.json")
    #   CSV name = DataPlayersP001Session1.csv

    rel = json_path.relative_to(base_dir)
    # we skip the actual file name (last part) and use only folder names
    components = [base_dir.name] + list(rel.parts[:-1])

    flat_name = "".join(part.replace(" ", "") for part in components)
    return OUTPUT_DIR / f"{flat_name}.csv"


def convert_single_file(json_path: Path, csv_path: Path):
    data = load_json(json_path)
    clean_data = convert_structure(data)
    df = json_to_dataframe(clean_data)
    save_dataframe_as_csv(df, csv_path)
    print(f"✅ Converted {json_path} → {csv_path}")


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

    print("🎉 Done converting all matching files.")


if __name__ == "__main__":
    main()
