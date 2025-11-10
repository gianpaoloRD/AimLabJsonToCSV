import json
import csv
from pathlib import Path


# -------------------------------
# Load JSON file from disk
# -------------------------------
def load_json(path: Path) -> dict:
    # Opens the given JSON file and returns its content as a Python dictionary.
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


# -------------------------------
# Flatten a specific section of the JSON
# -------------------------------
def flatten_section(data: dict, section: str, prefix: str) -> dict:
    """
    Takes one top-level section from the JSON (e.g. 'Player', 'Targets')
    and flattens all nested data into key-value pairs.
    Example:
        Player.Position.X = 0.23
        Player.Position.Y = 0.98
    """
    root = data.get(section)
    if root is None:
        return {}
    flat = {}
    _flatten_obj(root, prefix, flat)  # Recursive helper
    return flat


# -------------------------------
# Recursive flattening helper
# -------------------------------
def _flatten_obj(obj, prefix: str, out: dict):
    """
    Recursively walks through nested dicts and lists to produce a flat dictionary.
    Keys are built using dot notation (e.g., Player.Position.X).
    """
    # If the current object is a dictionary → recurse on each key/value
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_prefix = f"{prefix}.{k}" if prefix else k
            _flatten_obj(v, new_prefix, out)

    # If it's a list → handle it differently
    elif isinstance(obj, list):
        # If it's empty, record an empty string
        if not obj:
            out[prefix] = ""
            return

        # If the list contains dictionaries → index them (e.g., Targets.0.X)
        if all(isinstance(it, dict) for it in obj):
            for i, item in enumerate(obj):
                new_prefix = f"{prefix}.{i}"
                _flatten_obj(item, new_prefix, out)

        # If it's a list of simple values (numbers, strings) → join them into one comma-separated string
        elif all(not isinstance(it, (dict, list)) for it in obj):
            out[prefix] = ",".join(map(str, obj))

        # If it's a mixed list (some dicts, some primitives) → stringify everything
        else:
            out[prefix] = ",".join(map(str, obj))

    # If it's a single primitive value (int, float, string, bool)
    else:
        out[prefix] = obj


# -------------------------------
# Extract time-series data from Stats (special case)
# -------------------------------
def extract_stats_series(data: dict) -> list[dict]:
    """
    Extracts accuracy and score arrays from Stats into individual rows
    (used for time-series data where we need one row per sample).
    """
    stats = data.get("Stats", {})
    acc = stats.get("Accuracy", {})
    sco = stats.get("Score", {})

    acc_keys = acc.get("Keys", [])
    acc_vals = acc.get("Values", [])
    sco_keys = sco.get("Keys", [])
    sco_vals = sco.get("Values", [])

    # Determine how many rows are needed (max length among all arrays)
    max_len = max(len(acc_keys), len(acc_vals), len(sco_keys), len(sco_vals))
    rows = []

    # Build each row with corresponding Accuracy and Score values
    for i in range(max_len):
        rows.append({
            "Index": i,
            "Stats.Accuracy.Key": acc_keys[i] if i < len(acc_keys) else "",
            "Stats.Accuracy.Value": acc_vals[i] if i < len(acc_vals) else "",
            "Stats.Score.Key": sco_keys[i] if i < len(sco_keys) else "",
            "Stats.Score.Value": sco_vals[i] if i < len(sco_vals) else "",
        })
    return rows


# -------------------------------
# Collect all Stats column names (summary + series)
# -------------------------------
def list_stats_columns(data: dict) -> list[str]:
    stats_flat = flatten_section(data, "Stats", "Stats")
    series_rows = extract_stats_series(data)
    cols = set(stats_flat.keys())
    if series_rows:
        cols.update(series_rows[0].keys())
    return sorted(cols)


# -------------------------------
# Build full list of CSV column names
# -------------------------------
def build_fieldnames(series_rows: list[dict], summary: dict) -> list[str]:
    """
    Returns the full list of column names that will appear in the CSV file.
    If we have time-series rows, also include Index and Accuracy/Score keys.
    """
    if not series_rows:
        return sorted(summary.keys())

    base_series_fields = [
        "Index",
        "Stats.Accuracy.Key",
        "Stats.Accuracy.Value",
        "Stats.Score.Key",
        "Stats.Score.Value",
    ]
    fields = set(summary.keys())
    fields.update(base_series_fields)
    return sorted(fields)


# -------------------------------
# Write only summary data (no time-series)
# -------------------------------
def write_summary_csv(path: Path, summary: dict):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary.keys()))
        writer.writeheader()
        writer.writerow(summary)


# -------------------------------
# Write both time-series + summary data
# -------------------------------
def write_series_csv(path: Path, series_rows: list[dict], summary: dict):
    fieldnames = build_fieldnames(series_rows, summary)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in series_rows:
            # Merge static info (Stats, Player, Targets, Events) into every time-series row
            full_row = {**row, **summary}
            writer.writerow(full_row)


# -------------------------------
# Main workflow
# -------------------------------
def main():
    # Input and output file paths
    src = Path("adapting/play_01.pretty.json")
    out_csv = Path("adapting/stats_all.csv")

    # Load the JSON file into memory
    data = load_json(src)

    # Flatten all main sections (the “big 4”)
    stats_flat = flatten_section(data, "Stats", "Stats")
    player_flat = flatten_section(data, "Player", "Player")
    targets_flat = flatten_section(data, "Targets", "Targets")
    events_flat = flatten_section(data, "Events", "Events")  # ← the last main section

    # Combine all sections into a single dictionary for writing
    merged_summary = {
        **stats_flat,
        **player_flat,
        **targets_flat,
        **events_flat,
    }

    # Extract Stats time-series rows (Accuracy & Score)
    stats_series = extract_stats_series(data)

    # Print columns found in each section
    print("Stats columns pulled:")
    for c in list_stats_columns(data):
        print("  -", c)

    print("Player columns pulled:")
    for c in sorted(player_flat.keys()):
        print("  -", c)

    print("Targets columns pulled:")
    for c in sorted(targets_flat.keys()):
        print("  -", c)

    print("Events columns pulled:")
    for c in sorted(events_flat.keys()):
        print("  -", c)

    # Write CSV depending on whether there are time-series rows or not
    if not stats_series:
        write_summary_csv(out_csv, merged_summary)
        print(f"✅ wrote summary-only CSV to {out_csv}")
    else:
        write_series_csv(out_csv, stats_series, merged_summary)
        print(f"✅ wrote {len(stats_series)} rows to {out_csv}")


# Entry point
if __name__ == "__main__":
    main()
