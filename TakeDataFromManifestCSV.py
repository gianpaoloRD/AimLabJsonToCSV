import  pandas as pd
from pathlib import Path

def extract_columns(input_path: Path, output_path: Path, columns_to_keep: list[str]):
    # Read the original CSV
    df = pd.read_csv(input_path)

    # Filter only the columns that exist in the file
    valid_columns = [col for col in columns_to_keep if col in df.columns]

    # Warn if some requested columns were missing
    missing = [col for col in columns_to_keep if col not in df.columns]
    if missing:
        print(f"⚠️ Missing columns (not found in CSV): {missing}")

    # Create new DataFrame with only desired columns
    filtered_df = df[valid_columns]

    # Save to new CSV
    filtered_df.to_csv(output_path, index=False)
    print(f"✅ Extracted {len(valid_columns)} columns → Saved to {output_path}")




def main(input_path: Path, output_path: Path):
    columns_to_keep = [
        "duration",
        "endedAt",
        "performanceData.ValueMap",
        "performanceData.accTotal",
        "performanceData.killTotal",
        "performanceData.killsPerSec",
        "performanceData.rtB0",
        "performanceData.rtB1",
        "performanceData.rtB2",
        "performanceData.rtB3",
        "performanceData.rtB4",
        "performanceData.rtB5",
        "performanceData.rtB6",
        "performanceData.rtB7",
        "performanceData.rtTotal",
        "performanceData.shotsTotal",
        "performanceData.targetsTotal",
        "playDuration",
        "score"
    ]
    extract_columns(input_path, output_path,columns_to_keep)
    print(f"✅ Converted JSON saved to {output_path}")


if __name__ == "__main__":
    input_file = Path("aimlab_sample.csv")
    output_file = Path("DataExtractedFromManifest.csv")
    main(input_file, output_file)
