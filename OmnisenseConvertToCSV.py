from pathlib import Path
from converter import load_json, convert_structure, save_json, json_to_dataframe, save_dataframe_as_csv


def main(input_path: Path, output_path: Path):
    data = load_json(input_path)
    clean_data = convert_structure(data)
    clean_data = json_to_dataframe(clean_data)
    save_dataframe_as_csv(clean_data,output_path)
    print(f"✅ Converted JSON saved to {output_path}")


if __name__ == "__main__":
    input_file = Path("Input/OmniSenseSettingsLOGI.json")
    output_file = Path("OmniSenseSettingsLOGI.csv")
    main(input_file, output_file)
