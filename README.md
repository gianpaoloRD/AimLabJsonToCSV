# \# RobJsonConvert – JSON ➜ Wide CSV ➜ Target Files ➜ Concatenated CSV

# \# RobJsonConvert – JSON ➜ Wide CSV ➜ Target Files ➜ Concatenated CSV

# 

# This repo/process converts exported game/telemetry \*\*JSON\*\* files into:

# 1\) \*\*One wide CSV\*\* per JSON (all `{key\[], value\[]}` series aligned on `time`, dot-path headers).

# 2\) \*\*One CSV per target\*\* (columns that start with `targets.<ID>.`), trimming empty leading rows.

# 3\) \*\*One long concatenated CSV\*\* that stacks selected target files with `time`, numeric `target`, and a `tags` label like `target.<ID>`.

# 

# The pipeline also includes \*\*static target fields\*\* like `spawnTime` and `destroyTime` and correctly maps target columns using the \*\*true `targets\[i].id`\*\*, not the array index.

# 

# ---

# 

# \## Key Features

# 

# \- \*\*ID mapping:\*\* Columns under `targets\[...]` use `targets\[i].id` as the identifier (not the array index).

# \- \*\*Zero‑padding:\*\* Only IDs \*\*0–9\*\* are padded (e.g., `targets.00.\* … targets.09.\*`) when `pad\_targets=True`. IDs ≥10 are unchanged.

# \- \*\*Static fields:\*\* Adds per-target scalars to the wide CSV (default: `spawnTime`, `destroyTime`, `timeToLive`, `type`), forward-filled across rows.

# \- \*\*Empty trimming:\*\* Split step can trim \*\*leading\*\* empty rows; can also treat placeholders like `99999` as empty.

# \- \*\*Concatenation:\*\* Produces a tidy CSV with columns: `time, target, tags, …normalized columns…` (prefix `targets.<ID>.` removed in the long file).

# \- \*\*UTF‑8 CSVs:\*\* All files are written using UTF‑8 encoding.

# 

# ---

# 

# \## Folder Layout

# 

# By convention:

# ```

# FilesInput/        # put your .json files here

# FilesOutput/       # wide CSVs (one per JSON)

# TargetFiles/       # per-JSON subfolders with per-target CSVs

# ConcatOutputs/     # concatenated CSVs per JSON

# ```

# 

# You can change these folder names in the helper function parameters.

# 

# ---

# 

# \## Requirements

# 

# \- Python 3.8+ (tested on 3.12)

# \- Standard library only (no external dependencies).

# 

# ---

# 

# \## Core Functions (signatures)

# 

# ```python

# json\_series\_to\_one\_csv(src, out\_path, fill\_forward=True, pad\_targets=False,

# &nbsp;                      include\_target\_statics=("spawnTime","destroyTime","timeToLive","type"))

# ```

# Converts one JSON to one \*\*wide CSV\*\*, aligning all `{key\[], value\[]}` series on `time`. Uses `targets\[i].id` for headers under `targets.\*`. When `pad\_targets=True`, pads only 0–9.

# 

# ```python

# split\_targets\_csv(in\_csv, out\_dir=None, include\_time=True,

# &nbsp;                 empty\_policy="all",  # "leading" | "all" | "none"

# &nbsp;                 empty\_tokens=("", "NA", "NaN"),

# &nbsp;                 treat\_as\_empty\_tokens=None,

# &nbsp;                 pad\_single\_digit=True)

# ```

# Splits a wide CSV into \*\*one file per target\*\*. When `pad\_single\_digit=True`, filenames and headers inside are normalized so `1 ➜ 01` … `9 ➜ 09`. `empty\_policy="leading"` trims only leading empty rows per target (good to remove the white gaps). Use `treat\_as\_empty\_tokens=\["99999"]` to drop those as empty.

# 

# ```python

# concat\_target\_csvs(inputs, out\_csv)

# ```

# Concatenates all `targets.<ID>\_.csv` files in a folder into a single long CSV with columns: `time, target, tags, <union of normalized columns>`.

# \- `target` is numeric (e.g., `105`).

# \- `tags` is the textual label `target.<ID>` (no padding).

# 

# ```python

# run\_pipeline\_for\_folder(in\_dir="FilesInput",

# &nbsp;                       out\_dir="FilesOutput",

# &nbsp;                       targets\_root="TargetFiles",

# &nbsp;                       concat\_root="ConcatOutputs",

# &nbsp;                       fill\_forward=True,

# &nbsp;                       pad\_targets=True,

# &nbsp;                       empty\_policy="leading",

# &nbsp;                       treat\_as\_empty\_tokens=("99999",),

# &nbsp;                       pad\_single\_digit=True,

# &nbsp;                       pattern="\*.json")

# ```

# Runs the whole pipeline over every JSON in `in\_dir`, writing:

# \- `FilesOutput/<name>.csv` (wide CSV),

# \- `TargetFiles/<name>/targets.<ID>\_.csv` (per-target files),

# \- `ConcatOutputs/targets\_<name>\_concat.csv` (long CSV).

# 

# Returns a list of concatenated CSV paths.

# 

# ---

# 

# \## Quick Start

# 

# 1\. Put your `.json` files into `FilesInput/`.

# 2\. Call the batch runner:

# 

# ```python

# run\_pipeline\_for\_folder(

# &nbsp;   in\_dir="FilesInput",

# &nbsp;   out\_dir="FilesOutput",

# &nbsp;   targets\_root="TargetFiles",

# &nbsp;   concat\_root="ConcatOutputs",

# &nbsp;   fill\_forward=True,          # forward-fill missing values in wide CSV

# &nbsp;   pad\_targets=True,           # only 0–9 padded in headers under targets.\*

# &nbsp;   empty\_policy="leading",     # trim only leading empties in per-target CSVs

# &nbsp;   treat\_as\_empty\_tokens=("99999",),  # treat 99999 as empty

# &nbsp;   pad\_single\_digit=True       # normalize per-target filenames/headers to 01..09

# )

# ```

# 

# After it runs, check:

# \- `FilesOutput/<file>.csv` for the wide table,

# \- `TargetFiles/<file>/targets.<ID>\_.csv` for per-target series,

# \- `ConcatOutputs/targets\_<file>\_concat.csv` for the stacked CSV.

# 

# ---

# 

# \## Notes \& Tips

# 

# \- \*\*Headers \& IDs\*\*

# &nbsp; - The wide CSV uses real `targets\[i].id`. If the original JSON has mixed ordering (e.g., `targets\[0].id = 20`), the header will still be `targets.20.\*` based on the `id`.

# &nbsp; - Only IDs 0–9 are padded in the \*\*headers\*\* (when `pad\_targets=True`). Filenames in the split step can also be normalized via `pad\_single\_digit=True`.

# 

# \- \*\*Statics\*\*

# &nbsp; - Add/remove static fields with `include\_target\_statics=(...)` in `json\_series\_to\_one\_csv`.

# 

# \- \*\*Empty rows\*\*

# &nbsp; - `empty\_policy="leading"` removes only the empty rows at the start of each target file (keeps internal gaps).

# &nbsp; - To remove all-empty rows everywhere, use `empty\_policy="all"`.

# &nbsp; - Add tokens like `"99999"` to `treat\_as\_empty\_tokens` so placeholder rows disappear.

# 

# \- \*\*Ordering\*\*

# &nbsp; - The splitter writes files in \*\*numeric target ID\*\* order.

# &nbsp; - The concatenator keeps file order; if you want global time ordering, modify it to sort by `time`.

# 

# \- \*\*Windows paths\*\*

# &nbsp; - Use raw strings or forward slashes (`"FilesInput/file.json"`). The code already uses `pathlib` for portability.

# 

# \- \*\*Large files\*\*

# &nbsp; - The wide CSV step loads the JSON in memory. If your JSONs are huge, consider streaming/iterative parsing (not provided here).

# 

# ---

# 

# \## Minimal Example

# 

# ```python

# \# Single file end-to-end

# merged = json\_series\_to\_one\_csv("FilesInput/sample.json", "FilesOutput/sample.csv", fill\_forward=True, pad\_targets=True)

# split\_targets\_csv(merged, out\_dir="TargetFiles/sample", empty\_policy="leading", treat\_as\_empty\_tokens=\["99999"], pad\_single\_digit=True)

# concat\_target\_csvs("TargetFiles/sample", "ConcatOutputs/targets\_sample\_concat.csv")

# 

# \# Batch

# run\_pipeline\_for\_folder("FilesInput","FilesOutput","TargetFiles","ConcatOutputs")

# ```

# 

# ---

# 

# \## Troubleshooting

# 

# \- \*\*ValueError: No 'time' column\*\*  

# &nbsp; Your wide CSV must have a `time` column (first column). Ensure you generated it with `json\_series\_to\_one\_csv` from this project.

# 

# \- \*\*Mixed `targets.1.\*` vs `targets.01.\*`\*\*  

# &nbsp; Use `pad\_targets=True` when building the wide CSV \*\*and\*\* `pad\_single\_digit=True` when splitting.

# 

# \- \*\*Unexpected target labeling (`target.020`)\*\*  

# &nbsp; That happens if something else padded the label. This code keeps `tags` as plain `target.<ID>` (no padding), while padding applies only to headers/filenames where requested.

# 

# ---

# 

# \## License

# 

# MIT



# This repo/process converts exported game/telemetry \*\*JSON\*\* files into:

# 1\) \*\*One wide CSV\*\* per JSON (all `{key\[], value\[]}` series aligned on `time`, dot-path headers).

# 2\) \*\*One CSV per target\*\* (columns that start with `targets.<ID>.`), trimming empty leading rows.

# 3\) \*\*One long concatenated CSV\*\* that stacks selected target files with `time`, numeric `target`, and a `tags` label like `target.<ID>`.

# 

# The pipeline also includes \*\*static target fields\*\* like `spawnTime` and `destroyTime` and correctly maps target columns using the \*\*true `targets\[i].id`\*\*, not the array index.

# 

# ---

# 

# \## Key Features

# 

# \- \*\*ID mapping:\*\* Columns under `targets\[...]` use `targets\[i].id` as the identifier (not the array index).

# \- \*\*Zero‑padding:\*\* Only IDs \*\*0–9\*\* are padded (e.g., `targets.00.\* … targets.09.\*`) when `pad\_targets=True`. IDs ≥10 are unchanged.

# \- \*\*Static fields:\*\* Adds per-target scalars to the wide CSV (default: `spawnTime`, `destroyTime`, `timeToLive`, `type`), forward-filled across rows.

# \- \*\*Empty trimming:\*\* Split step can trim \*\*leading\*\* empty rows; can also treat placeholders like `99999` as empty.

# \- \*\*Concatenation:\*\* Produces a tidy CSV with columns: `time, target, tags, …normalized columns…` (prefix `targets.<ID>.` removed in the long file).

# \- \*\*UTF‑8 CSVs:\*\* All files are written using UTF‑8 encoding.

# 

# ---

# 

# \## Folder Layout

# 

# By convention:

# ```

# FilesInput/        # put your .json files here

# FilesOutput/       # wide CSVs (one per JSON)

# TargetFiles/       # per-JSON subfolders with per-target CSVs

# ConcatOutputs/     # concatenated CSVs per JSON

# ```

# 

# You can change these folder names in the helper function parameters.

# 

# ---

# 

# \## Requirements

# 

# \- Python 3.8+ (tested on 3.12)

# \- Standard library only (no external dependencies).

# 

# ---

# 

# \## Core Functions (signatures)

# 

# ```python

# json\_series\_to\_one\_csv(src, out\_path, fill\_forward=True, pad\_targets=False,

# &nbsp;                      include\_target\_statics=("spawnTime","destroyTime","timeToLive","type"))

# ```

# Converts one JSON to one \*\*wide CSV\*\*, aligning all `{key\[], value\[]}` series on `time`. Uses `targets\[i].id` for headers under `targets.\*`. When `pad\_targets=True`, pads only 0–9.

# 

# ```python

# split\_targets\_csv(in\_csv, out\_dir=None, include\_time=True,

# &nbsp;                 empty\_policy="all",  # "leading" | "all" | "none"

# &nbsp;                 empty\_tokens=("", "NA", "NaN"),

# &nbsp;                 treat\_as\_empty\_tokens=None,

# &nbsp;                 pad\_single\_digit=True)

# ```

# Splits a wide CSV into \*\*one file per target\*\*. When `pad\_single\_digit=True`, filenames and headers inside are normalized so `1 ➜ 01` … `9 ➜ 09`. `empty\_policy="leading"` trims only leading empty rows per target (good to remove the white gaps). Use `treat\_as\_empty\_tokens=\["99999"]` to drop those as empty.

# 

# ```python

# concat\_target\_csvs(inputs, out\_csv)

# ```

# Concatenates all `targets.<ID>\_.csv` files in a folder into a single long CSV with columns: `time, target, tags, <union of normalized columns>`.

# \- `target` is numeric (e.g., `105`).

# \- `tags` is the textual label `target.<ID>` (no padding).

# 

# ```python

# run\_pipeline\_for\_folder(in\_dir="FilesInput",

# &nbsp;                       out\_dir="FilesOutput",

# &nbsp;                       targets\_root="TargetFiles",

# &nbsp;                       concat\_root="ConcatOutputs",

# &nbsp;                       fill\_forward=True,

# &nbsp;                       pad\_targets=True,

# &nbsp;                       empty\_policy="leading",

# &nbsp;                       treat\_as\_empty\_tokens=("99999",),

# &nbsp;                       pad\_single\_digit=True,

# &nbsp;                       pattern="\*.json")

# ```

# Runs the whole pipeline over every JSON in `in\_dir`, writing:

# \- `FilesOutput/<name>.csv` (wide CSV),

# \- `TargetFiles/<name>/targets.<ID>\_.csv` (per-target files),

# \- `ConcatOutputs/targets\_<name>\_concat.csv` (long CSV).

# 

# Returns a list of concatenated CSV paths.

# 

# ---

# 

# \## Quick Start

# 

# 1\. Put your `.json` files into `FilesInput/`.

# 2\. Call the batch runner:

# 

# ```python

# run\_pipeline\_for\_folder(

# &nbsp;   in\_dir="FilesInput",

# &nbsp;   out\_dir="FilesOutput",

# &nbsp;   targets\_root="TargetFiles",

# &nbsp;   concat\_root="ConcatOutputs",

# &nbsp;   fill\_forward=True,          # forward-fill missing values in wide CSV

# &nbsp;   pad\_targets=True,           # only 0–9 padded in headers under targets.\*

# &nbsp;   empty\_policy="leading",     # trim only leading empties in per-target CSVs

# &nbsp;   treat\_as\_empty\_tokens=("99999",),  # treat 99999 as empty

# &nbsp;   pad\_single\_digit=True       # normalize per-target filenames/headers to 01..09

# )

# ```

# 

# After it runs, check:

# \- `FilesOutput/<file>.csv` for the wide table,

# \- `TargetFiles/<file>/targets.<ID>\_.csv` for per-target series,

# \- `ConcatOutputs/targets\_<file>\_concat.csv` for the stacked CSV.

# 

# ---

# 

# \## Notes \& Tips

# 

# \- \*\*Headers \& IDs\*\*

# &nbsp; - The wide CSV uses real `targets\[i].id`. If the original JSON has mixed ordering (e.g., `targets\[0].id = 20`), the header will still be `targets.20.\*` based on the `id`.

# &nbsp; - Only IDs 0–9 are padded in the \*\*headers\*\* (when `pad\_targets=True`). Filenames in the split step can also be normalized via `pad\_single\_digit=True`.

# 

# \- \*\*Statics\*\*

# &nbsp; - Add/remove static fields with `include\_target\_statics=(...)` in `json\_series\_to\_one\_csv`.

# 

# \- \*\*Empty rows\*\*

# &nbsp; - `empty\_policy="leading"` removes only the empty rows at the start of each target file (keeps internal gaps).

# &nbsp; - To remove all-empty rows everywhere, use `empty\_policy="all"`.

# &nbsp; - Add tokens like `"99999"` to `treat\_as\_empty\_tokens` so placeholder rows disappear.

# 

# \- \*\*Ordering\*\*

# &nbsp; - The splitter writes files in \*\*numeric target ID\*\* order.

# &nbsp; - The concatenator keeps file order; if you want global time ordering, modify it to sort by `time`.

# 

# \- \*\*Windows paths\*\*

# &nbsp; - Use raw strings or forward slashes (`"FilesInput/file.json"`). The code already uses `pathlib` for portability.

# 

# \- \*\*Large files\*\*

# &nbsp; - The wide CSV step loads the JSON in memory. If your JSONs are huge, consider streaming/iterative parsing (not provided here).

# 

# ---

# 

# \## Minimal Example

# 

# ```python

# \# Single file end-to-end

# merged = json\_series\_to\_one\_csv("FilesInput/sample.json", "FilesOutput/sample.csv", fill\_forward=True, pad\_targets=True)

# split\_targets\_csv(merged, out\_dir="TargetFiles/sample", empty\_policy="leading", treat\_as\_empty\_tokens=\["99999"], pad\_single\_digit=True)

# concat\_target\_csvs("TargetFiles/sample", "ConcatOutputs/targets\_sample\_concat.csv")

# 

# \# Batch

# run\_pipeline\_for\_folder("FilesInput","FilesOutput","TargetFiles","ConcatOutputs")

# ```

# 

# ---

# 

# \## Troubleshooting

# 

# \- \*\*ValueError: No 'time' column\*\*  

# &nbsp; Your wide CSV must have a `time` column (first column). Ensure you generated it with `json\_series\_to\_one\_csv` from this project.

# 

# \- \*\*Mixed `targets.1.\*` vs `targets.01.\*`\*\*  

# &nbsp; Use `pad\_targets=True` when building the wide CSV \*\*and\*\* `pad\_single\_digit=True` when splitting.

# 

# \- \*\*Unexpected target labeling (`target.020`)\*\*  

# &nbsp; That happens if something else padded the label. This code keeps `tags` as plain `target.<ID>` (no padding), while padding applies only to headers/filenames where requested.

# 

# ---

# 

# \## License

# 

# MIT



