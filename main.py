import csv, re, os, glob
from pathlib import Path
from collections import defaultdict, deque


def json_series_to_one_csv(src, out_path, fill_forward=True, pad_targets=False,
                           include_target_statics=("spawnTime","destroyTime","timeToLive","type")):
    import json, csv
    from pathlib import Path

    def is_series(n):
        return isinstance(n, dict) and "key" in n and "value" in n and isinstance(n["key"], list)

    targets_idx_to_id = {}

    def id_label(n):
        try:
            n = int(n)
            return f"{n:02d}" if pad_targets and 0 <= n <= 9 else str(n)
        except Exception:
            return str(n)

    def safe_col(parts):
        out = []
        for i, p in enumerate(parts):
            s = str(p)
            if i > 0 and parts[i-1] == "targets":
                if s in targets_idx_to_id:
                    s = targets_idx_to_id[s]
                elif s.isdigit():
                    s = id_label(int(s))
            out.append(s)
        return ".".join(out)

    def flatten_value(v):
        if isinstance(v, dict):
            ks = sorted(v.keys())
            return {k: v[k] for k in ks}
        if isinstance(v, list):
            return {f"value_{i}": v[i] for i in range(len(v))}
        return {"value": v}

    if isinstance(src, (str, Path)):
        with open(src, "r") as f:
            data = json.load(f)
    else:
        data = src

    columns = {}            # col_name -> {time: value}
    all_times = set()
    static_to_add = []      # list of (path_parts, value)

    def record_series(path_parts, keys, vals):
        if not keys or not vals:
            return
        first = flatten_value(vals[0])
        subcols = sorted(first.keys())
        maps = {sc: {} for sc in subcols}
        n = min(len(keys), len(vals))
        for i in range(n):
            t = keys[i]
            fv = flatten_value(vals[i])
            for sc in subcols:
                maps[sc][t] = fv.get(sc, None)
        for sc, tm in maps.items():
            col = safe_col(path_parts + [sc])
            columns[col] = tm
            all_times.update(tm.keys())

    def walk(node, path_parts):
        # capture targets[idx].id to map index -> true id (with optional padding)
        if isinstance(node, dict) and len(path_parts) >= 2 and path_parts[-2] == "targets":
            idx_token = path_parts[-1]
            if idx_token.isdigit() and "id" in node:
                try:
                    targets_idx_to_id[idx_token] = id_label(int(node["id"]))
                except Exception:
                    targets_idx_to_id[idx_token] = str(node["id"])
            # collect static scalar fields at this target object
            for k in include_target_statics:
                if k in node and not is_series(node[k]):
                    static_to_add.append((path_parts + [k], node[k]))

        if is_series(node):
            record_series(path_parts, node["key"], node["value"])
            v = node.get("value")
            if isinstance(v, list):
                for i, vi in enumerate(v):
                    walk(vi, path_parts + [f"value_{i}"])
            return

        if isinstance(node, dict):
            for k, v in node.items():
                walk(v, path_parts + [k])
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, path_parts + [str(i)])

    walk(data, [])

    # decide timeline
    times = sorted(all_times, key=float)
    if not times:
        times = [0.0]  # fallback if no series present

    # inject static fields as columns set at the first timestamp (then forward-fill)
    t0 = times[0]
    for parts, val in static_to_add:
        col = safe_col(parts)
        if col not in columns:
            columns[col] = {}
        # only set once (in case duplicates)
        if t0 not in columns[col]:
            columns[col][t0] = val

    col_names = sorted(columns.keys())

    out_path = Path(out_path)
    with open(out_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["time"] + col_names)
        last = {c: None for c in col_names}
        for t in times:
            row = [format(float(t), ".15g")]
            for c in col_names:
                v = columns[c].get(t, None)
                if v is None and fill_forward:
                    v = last[c]
                row.append(v)
                if v is not None:
                    last[c] = v
            w.writerow(row)
    return str(out_path)







def split_targets_csv(in_csv, out_dir=None, include_time=True,
                      empty_policy="all",
                      empty_tokens=("", "NA", "NaN"),
                      treat_as_empty_tokens=None,
                      pad_single_digit=True):
    in_csv = Path(in_csv)
    out_dir = Path(out_dir) if out_dir else in_csv.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    empty_set = set(str(s).strip() for s in empty_tokens)
    if treat_as_empty_tokens:
        empty_set |= set(str(s).strip() for s in treat_as_empty_tokens)

    def is_empty(vals):
        return all((v is None) or (str(v).strip() in empty_set) for v in vals)

    rx = re.compile(r'^(targets\.)(\d+)(\.)(.+)$', re.ASCII)

    with open(in_csv, newline='', encoding='utf-8') as f:
        r = csv.reader(f)
        header = next(r)

        time_idx = next((i for i, h in enumerate(header)
                         if include_time and h.lower() == "time"), None)

        groups = defaultdict(list)  # gid_int -> list of (col_idx, rewritten_header)
        for i, name in enumerate(header):
            m = rx.match(name)
            if not m:
                continue
            gid_int = int(m.group(2))
            gid_str = f"{gid_int:02d}" if pad_single_digit and gid_int < 10 else str(gid_int)
            new_header = f"{m.group(1)}{gid_str}{m.group(3)}{m.group(4)}"
            groups[gid_int].append((i, new_header))

        writers, paths, counts = {}, {}, {gid: 0 for gid in groups}
        buffers = {gid: deque() for gid in groups} if empty_policy == "leading" else None
        seen_real = {gid: False for gid in groups} if empty_policy == "leading" else None

        try:
            for gid in sorted(groups):
                idxs_headers = groups[gid]
                gid_str = f"{gid:02d}" if pad_single_digit and gid < 10 else str(gid)
                p = out_dir / f"targets.{gid_str}_.csv"
                fh = open(p, "w", newline="", encoding="utf-8")
                w = csv.writer(fh)
                cols = []
                if time_idx is not None:
                    cols.append(header[time_idx])
                cols += [nh for (_i, nh) in idxs_headers]
                w.writerow(cols)
                writers[gid] = (w, fh, [i for (i, _nh) in idxs_headers])
                paths[gid] = str(p)

            for row in r:
                for gid, (w, _fh, idxs) in writers.items():
                    vals = [row[i] for i in idxs]
                    if empty_policy == "none":
                        out_row = ([row[time_idx]] if time_idx is not None else []) + vals
                        w.writerow(out_row); counts[gid] += 1
                        continue
                    if empty_policy == "all":
                        if is_empty(vals):
                            continue
                        out_row = ([row[time_idx]] if time_idx is not None else []) + vals
                        w.writerow(out_row); counts[gid] += 1
                        continue
                    if is_empty(vals) and not seen_real[gid]:
                        buffers[gid].append((row[time_idx] if time_idx is not None else None, vals))
                        continue
                    else:
                        if not seen_real[gid]:
                            seen_real[gid] = True
                        out_row = ([row[time_idx]] if time_idx is not None else []) + vals
                        w.writerow(out_row); counts[gid] += 1
        finally:
            for w, fh, _ in writers.values():
                fh.close()

        for gid, n in list(counts.items()):
            if n == 0:
                try:
                    os.remove(paths[gid]); del paths[gid]
                except OSError:
                    pass

    return [paths[k] for k in sorted(paths)]


def concat_target_csvs(inputs, out_csv):
    if isinstance(inputs, (str, Path)) and os.path.isdir(str(inputs)):
        files = sorted(glob.glob(str(Path(inputs) / "targets.*_.csv")))
    elif isinstance(inputs, (str, Path)) and not isinstance(inputs, list):
        files = [str(inputs)]
    else:
        files = [str(p) for p in inputs]

    rx_file = re.compile(r"targets\.(\d+)_\.csv$")
    rx_col  = re.compile(r"^targets\.\d+\.")

    all_cols = set()
    meta = []
    for fp in files:
        with open(fp, newline="", encoding="utf-8") as f:
            r = csv.reader(f)
            hdr = next(r)
            t_idx = next((i for i,h in enumerate(hdr) if h.lower()=="time"), None)
            if t_idx is None:
                raise ValueError(f"No 'time' column in {fp}")
            cols = [(i, rx_col.sub("", h)) for i,h in enumerate(hdr) if i != t_idx]
            all_cols.update(c for _,c in cols)
            m = rx_file.search(os.path.basename(fp))
            tgt = m.group(1) if m else ""
            meta.append((fp, t_idx, cols, tgt))

    ordered_cols = sorted(all_cols)
    out_csv = str(out_csv)
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["time","target","tags"] + ordered_cols)
        for fp, t_idx, cols, tgt in meta:
            with open(fp, newline="", encoding="utf-8") as g:
                r = csv.reader(g)
                next(r)
                for row in r:
                    row_map = {cname: row[i] for i,cname in cols}
                    w.writerow([row[t_idx], tgt, f"target.{tgt}"] + [row_map.get(c, "") for c in ordered_cols])
    return out_csv


def run_pipeline_for_folder(in_dir="FilesInput",
                            out_dir="FilesOutput",
                            targets_root="TargetFiles",
                            concat_root="ConcatOutputs",
                            fill_forward=True,
                            pad_targets=True,
                            empty_policy="leading",
                            treat_as_empty_tokens=("99999",),
                            pad_single_digit=True,
                            pattern="*.json"):
    in_dir = Path(in_dir)
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    targets_root = Path(targets_root); targets_root.mkdir(parents=True, exist_ok=True)
    concat_root = Path(concat_root); concat_root.mkdir(parents=True, exist_ok=True)
    outputs = []
    for f in sorted(in_dir.glob(pattern)):
        if not f.is_file(): continue
        merged_csv = str(out_dir / (f.stem + ".csv"))
        json_series_to_one_csv(str(f), merged_csv, fill_forward=fill_forward, pad_targets=pad_targets)
        per_file_targets_dir = targets_root / f.stem
        per_file_targets_dir.mkdir(parents=True, exist_ok=True)
        split_targets_csv(merged_csv,
                          out_dir=str(per_file_targets_dir),
                          empty_policy=empty_policy,
                          treat_as_empty_tokens=list(treat_as_empty_tokens),
                          pad_single_digit=pad_single_digit)
        concat_csv = str(concat_root / f"targets_{f.stem}_concat.csv")
        concat_target_csvs(str(per_file_targets_dir), concat_csv)
        outputs.append(concat_csv)
    return outputs


run_pipeline_for_folder("FilesInput","FilesOutput","TargetFiles","ConcatOutputs")


'''
json_series_to_one_csv("FilesInput/041e297e-a32e-4819-a30e-a5d47c3e1dd4.json", "FilesOutput/merged.csv", fill_forward=True,pad_targets=True)

# trim only the leading blanks; also treat 99999 as empty
split_targets_csv("FilesOutput/merged.csv", out_dir="TargetFiles",
                  empty_policy="leading",
                  treat_as_empty_tokens=["99999"],
                  pad_single_digit=True)

# or concat everything in a folder
concat_target_csvs("TargetFiles", "targets_all_concat.csv")
'''
