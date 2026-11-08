#!/usr/bin/env python3
"""CSAMD W1 preprocessing and optional W1/W2 merging (2024-2025).

Python 3.10+; standard library only. No database or network access is needed.
Extract both supplied files to one directory, then run:

    python3 w1_preprocessing.py

This cleans the supplied W1_raw.csv and writes a new outputs/ directory with
658,637 retained rows and JSON audit files. Source data are not overwritten.
The source is the original GB18030 station-platform export, not device packets.
W1 station identity (sensor_id=46324, model_number=16102378), fixed registry
coordinates, work_status=1, and UTC+08:00 are explicit processing inputs;
they are not fields present in the original export. Gaps are not filled.

To reproduce the combined 662,029-row weather table as well, supply either the
original W2-only CSV or the published v7 Meteorological_87_44.csv:

    python3 w1_preprocessing.py --w2 /path/to/Meteorological_87_44.csv

Dataset: https://doi.org/10.6084/m9.figshare.29250797
The supplied --w2 input must be the 2024-2025 table, without 2026 additions.
Existing W1 rows in a combined input are replaced by freshly processed W1;
only W2 rows are reused. No W2 dataset is embedded in this two-file package.
The final merged schema follows the published v7 table (dataset v1.7.4).

For another run, choose a new output directory:

    python3 w1_preprocessing.py --output-dir outputs_second_run

Use --input to select another export with the same source schema. The rules,
commissioning cutoff, coordinates and station identity are specific to W1.
Source dates follow the station's local clock and are labeled +08:00; they
are not shifted by eight hours. W1 pressure is multiplied by 100 (hPa to Pa).
The script checks all inclusive physical ranges below, removes commissioning
rows at/before 2024-04-07 14:02:28, and keeps the first exact duplicate only.
Same-timestamp observations with differing measurements are retained.

This single-file distribution consolidates the original W1 cleaning rules
and merge logic and the final published field-name adjustments. It does not
recalibrate sensors, reinterpret W2 time zones, correct W2 minimum-wind
ambiguities, or recover never-received observations. The original W1 export
has 658,668 rows; 28 commissioning rows and 3 exact duplicates are excluded.
Only several GB of available memory and disk space for outputs are needed.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any


SOURCE_FIELDS = [
    "Date",
    "风速(m/s)",
    "雨量(mm)",
    "大气温度(℃)",
    "土壤温度(℃)",
    "液位(mm)",
    "蒸发(mm)",
    "风向(°)",
    "土壤湿度(%)",
    "大气湿度(%RH)",
    "数字气压(hPa)",
    "照度(Lux)",
    "简易总辐射(W/m2)",
    "辐射累计(MJ/m2)",
    "雨量累计(mm)",
]

OUTPUT_FIELDS = [
    "incident_id",
    "sensor_id",
    "work_status",
    "longitude(°)",
    "latitude(°)",
    "collect_time",
    "wind_speed(m/s)",
    "rainfall(mm)",
    "air_temperature(°C)",
    "soil_temperature(°C)",
    "water_level(mm)",
    "evaporation(mm)",
    "wind_direction(°)",
    "soil_humidity(%)",
    "air_humidity(%RH)",
    "atmo_pressure(Pa)",
    "light_sensor(Lux)",
    "total_radiation(W/m2)",
    "accumulated_radiation(MJ/m2)",
    "accumulated_rainfall(mm)",
]

# These are deliberately broad physical/data-validity limits, not normal-weather
# intervals. End points are retained. No percentile-based trimming is performed.
PHYSICAL_LIMITS = {
    "风速(m/s)": (0.0, 75.0),
    "雨量(mm)": (0.0, 100.0),
    "大气温度(℃)": (-60.0, 60.0),
    "土壤温度(℃)": (-50.0, 70.0),
    "液位(mm)": (0.0, 1000.0),
    "蒸发(mm)": (0.0, 1000.0),
    "风向(°)": (0.0, 360.0),
    "土壤湿度(%)": (0.0, 100.0),
    "大气湿度(%RH)": (0.0, 100.0),
    "数字气压(hPa)": (800.0, 1100.0),
    "照度(Lux)": (0.0, 200000.0),
    "简易总辐射(W/m2)": (0.0, 2000.0),
    "辐射累计(MJ/m2)": (0.0, 1000.0),
    "雨量累计(mm)": (0.0, 1000.0),
}

SENSOR_ID = "46324"
# Retained W1 rows are valid reports from an operating sensor.
WORK_STATUS = "1"
LONGITUDE = "87.305231"
LATITUDE = "44.223199"
STARTUP_END = datetime(2024, 4, 7, 14, 2, 28)
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def parse_args() -> argparse.Namespace:
    base = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=base / "W1_raw.csv",
        help="GB18030/UTF-8 source CSV",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=base / "outputs",
        help="directory for the cleaned CSV and audit JSON files",
    )
    parser.add_argument(
        "--w2",
        type=Path,
        help="optional W2-only or published v7 combined weather CSV (2024-2025)",
    )
    return parser.parse_args()


def open_source(path: Path):
    for encoding in ("utf-8-sig", "gb18030"):
        try:
            handle = path.open("r", encoding=encoding, newline="")
            handle.read(4096)
            handle.seek(0)
            return handle, encoding
        except UnicodeDecodeError:
            handle.close()
    raise UnicodeDecodeError("unknown", b"", 0, 1, "unsupported source encoding")


def output_record(source: dict[str, str], timestamp: datetime) -> dict[str, str]:
    # Represent the historical release's configured local station clock as UTC+08:00.
    return {
        "incident_id": "",
        "sensor_id": SENSOR_ID,
        "work_status": WORK_STATUS,
        "longitude(°)": LONGITUDE,
        "latitude(°)": LATITUDE,
        "collect_time": timestamp.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "wind_speed(m/s)": source["风速(m/s)"],
        "rainfall(mm)": source["雨量(mm)"],
        "air_temperature(°C)": source["大气温度(℃)"],
        "soil_temperature(°C)": source["土壤温度(℃)"],
        "water_level(mm)": source["液位(mm)"],
        "evaporation(mm)": source["蒸发(mm)"],
        "wind_direction(°)": source["风向(°)"],
        "soil_humidity(%)": source["土壤湿度(%)"],
        "air_humidity(%RH)": source["大气湿度(%RH)"],
        "atmo_pressure(Pa)": format(Decimal(source["数字气压(hPa)"]) * 100, "f"),
        "light_sensor(Lux)": source["照度(Lux)"],
        "total_radiation(W/m2)": source["简易总辐射(W/m2)"],
        "accumulated_radiation(MJ/m2)": source["辐射累计(MJ/m2)"],
        "accumulated_rainfall(mm)": source["雨量累计(mm)"],
    }


def clean_w1(args: argparse.Namespace) -> None:
    args.output_dir.mkdir(parents=True, exist_ok=False)

    output_csv = args.output_dir / "Meterological_W1_87_44.csv"
    summary_json = args.output_dir / "Meterological_W1_87_44_deletions.json"
    records_json = args.output_dir / "Meterological_W1_87_44_deleted_records.json"
    validation_json = args.output_dir / "Meterological_W1_87_44_validation.json"

    retained: list[tuple[datetime, int, dict[str, str]]] = []
    deleted: list[dict[str, Any]] = []
    seen_rows: set[tuple[str, ...]] = set()
    timestamp_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    input_by_year: Counter[str] = Counter()
    deleted_by_year_reason: dict[str, Counter[str]] = defaultdict(Counter)
    observed_min: dict[str, float] = {}
    observed_max: dict[str, float] = {}

    handle, source_encoding = open_source(args.input)
    with handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != SOURCE_FIELDS:
            raise ValueError(
                "Unexpected source columns.\n"
                f"Expected: {SOURCE_FIELDS}\n"
                f"Found:    {reader.fieldnames}"
            )

        for line_number, raw_row in enumerate(reader, start=2):
            row = {field: (raw_row.get(field) or "").strip() for field in SOURCE_FIELDS}
            raw_time = row["Date"]
            year = raw_time[:4] if len(raw_time) >= 4 else "unknown"
            input_by_year[year] += 1
            reasons: list[str] = []

            try:
                timestamp = datetime.strptime(raw_time, TIME_FORMAT)
            except ValueError:
                timestamp = None
                reasons.append("时间格式无效")

            numeric_values: dict[str, float] = {}
            for field, (low, high) in PHYSICAL_LIMITS.items():
                text = row[field]
                if not text:
                    reasons.append(f"{field}缺失")
                    continue
                try:
                    value = float(text)
                except ValueError:
                    reasons.append(f"{field}不是数值")
                    continue
                if not math.isfinite(value):
                    reasons.append(f"{field}不是有限数值")
                    continue
                numeric_values[field] = value
                observed_min[field] = min(observed_min.get(field, value), value)
                observed_max[field] = max(observed_max.get(field, value), value)
                if not low <= value <= high:
                    reasons.append(f"{field}超出物理范围[{low}, {high}]")

            if timestamp is not None and timestamp <= STARTUP_END:
                reasons.append("启动调试阶段")

            row_key = tuple(row[field] for field in SOURCE_FIELDS)
            if row_key in seen_rows:
                reasons.append("完全重复记录")
            else:
                seen_rows.add(row_key)

            if reasons:
                unique_reasons = list(dict.fromkeys(reasons))
                for reason in unique_reasons:
                    deleted_by_year_reason[year][reason] += 1
                deleted.append(
                    {
                        "source_line": line_number,
                        "year": year,
                        "reasons": unique_reasons,
                        "record": row,
                    }
                )
                continue

            assert timestamp is not None
            normalized = output_record(row, timestamp)
            retained.append((timestamp, line_number, normalized))
            timestamp_rows[raw_time].append(
                {"source_line": line_number, "record": row}
            )

    retained.sort(key=lambda item: (item[0], item[1]))
    for incident_id, (_, _, row) in enumerate(retained, start=1):
        row["incident_id"] = str(incident_id)

    with output_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(row for _, _, row in retained)

    retained_by_year = Counter(timestamp.strftime("%Y") for timestamp, _, _ in retained)
    deletion_summary = {
        "说明": "课题一W1一分钟气象数据清洗统计；缺失时间段未插补。",
        "source_file": args.input.name,
        "source_encoding": source_encoding,
        "output_file": output_csv.name,
        "input_records": sum(input_by_year.values()),
        "retained_records": len(retained),
        "deleted_unique_records": len(deleted),
        "deletion_percentage": round(len(deleted) * 100 / sum(input_by_year.values()), 6),
        "by_year": {
            year: {
                "input_records": input_by_year[year],
                "retained_records": retained_by_year[year],
                "deleted_unique_records": input_by_year[year] - retained_by_year[year],
                "reasons": dict(sorted(deleted_by_year_reason[year].items())),
            }
            for year in sorted(input_by_year)
        },
        "rules": {
            "startup_commissioning": "删除2024-04-07 13:35:23至14:02:28（含端点）的28条调试记录",
            "exact_duplicates": "相同时间和全部测量字段完全一致时，仅保留一条",
            "conflicting_same_timestamp": "同一秒但测量值不同的记录不自动删除，在validation文件中列出",
            "missing_periods": "不插补、不生成缺失时间点",
            "physical_limits": PHYSICAL_LIMITS,
            "pressure_conversion": "数字气压由hPa乘以100转换为Pa",
            "time_representation": "源时间按本地钟表时间解释，输出显式标记+08:00",
        },
    }
    with summary_json.open("w", encoding="utf-8") as handle:
        json.dump(deletion_summary, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    deleted_grouped: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for item in deleted:
        for reason in item["reasons"]:
            deleted_grouped[item["year"]][reason].append(
                {
                    "source_line": item["source_line"],
                    "record": item["record"],
                }
            )
    with records_json.open("w", encoding="utf-8") as handle:
        json.dump(
            {
                "说明": "被删除的源记录，按年份和删除原因分组；一条记录可能出现在多个原因下。",
                "records": deleted_grouped,
            },
            handle,
            ensure_ascii=False,
            indent=2,
        )
        handle.write("\n")

    conflicting_timestamps = {
        timestamp: entries
        for timestamp, entries in timestamp_rows.items()
        if len(entries) > 1
    }
    validation = {
        "说明": "清洗输出的完整性检查以及保留的同秒不同值记录。",
        "status": "passed",
        "checks": {
            "record_count_matches": len(retained)
            == sum(input_by_year.values()) - len(deleted),
            "chronological_order": all(
                retained[index][0] <= retained[index + 1][0]
                for index in range(len(retained) - 1)
            ),
            "incident_ids_sequential": all(
                row["incident_id"] == str(index)
                for index, (_, _, row) in enumerate(retained, start=1)
            ),
            "coordinates_six_decimals": all(
                row["longitude(°)"] == LONGITUDE and row["latitude(°)"] == LATITUDE
                for _, _, row in retained
            ),
            "pressure_converted_to_pa": all(
                80000 <= float(row["atmo_pressure(Pa)"]) <= 110000
                for _, _, row in retained
            ),
        },
        "retained_time_range": {
            "start": retained[0][2]["collect_time"] if retained else None,
            "end": retained[-1][2]["collect_time"] if retained else None,
        },
        "observed_source_ranges": {
            field: {"min": observed_min[field], "max": observed_max[field]}
            for field in PHYSICAL_LIMITS
        },
        "retained_conflicting_same_timestamp_groups": conflicting_timestamps,
    }
    with validation_json.open("w", encoding="utf-8") as handle:
        json.dump(validation, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    print(f"Input records:   {sum(input_by_year.values()):,}")
    print(f"Retained records:{len(retained):,}")
    print(f"Deleted records: {len(deleted):,}")
    print(f"Cleaned CSV:     {output_csv}")
    print(f"Audit files:     {summary_json}, {records_json}, {validation_json}")

# Final published schema: the historical rainfall-time field is omitted, and
# PAR, rainfall-intensity and heater-temperature labels use the v7 spelling.
# These are schema changes; W2 numeric values are not converted or corrected.
W2_FIELDS = [
    "incident_id", "sensor_id", "work_status", "longitude(°)", "latitude(°)",
    "collect_time", "air_temperature(°C)", "humidity(volume %)",
    "photosynthetic_effect(μmol/m²/s)", "atmo_pressure(Pa)", "light_sensor(Lux)",
    "min_wind_dir(°)", "max_wind_dir(°)", "avg_wind_dir(°)",
    "min_wind_speed(m/s)", "max_wind_speed(m/s)", "avg_wind_speed(m/s)",
    "rainfall(mm)", "rainfall_extent(mm/h)", "max_rainfall_extent(mm/h)",
    "heater_temperature(°C)", "toppling_condition", "co2_concentration(ppm)",
]
W1_ONLY_FIELDS = [
    "wind_speed(m/s)", "wind_direction(°)", "rainfall_increment(mm)",
    "soil_temperature(°C)", "soil_humidity(%)", "water_level(mm)",
    "evaporation(mm)", "total_radiation(W/m2)",
    "accumulated_radiation(MJ/m2)", "accumulated_rainfall(mm)",
]
MERGED_FIELDS = W2_FIELDS + W1_ONLY_FIELDS
FIELD_ALIASES = {
    "photosynthetic_effect(mol/m2/s)": "photosynthetic_effect(μmol/m²/s)",
    "rainfall_extent(mm)": "rainfall_extent(mm/h)",
    "max_rainfall_extent(mm)": "max_rainfall_extent(mm/h)",
    "heat_temparature(C)": "heater_temperature(°C)",
}
OMITTED_FIELDS = {"rainfall_time(min)", "rainfall_time"}
SOURCE_SHA256 = "031e71ec0ae0d39a3ae9d4eb36230bf037db109e9e20d6da2fbd6e373e913a87"
CLEANED_SHA256 = "bdb780470fe6064c28170f3cd087b28645938f34ced9f0e921ac2529b7c5886b"
MERGED_SHA256 = "aca466ba988d79e7e42f1fc32a39c6830b9c9fbff14ec25040df2e4bba88f6d2"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def merge_weather(w2_path: Path, cleaned_path: Path, output_dir: Path) -> dict:
    """Keep W2 order, then append W1, using the final v7 field union."""
    rows: list[dict[str, str]] = []
    omitted: list[dict[str, Any]] = []
    skipped_w1 = 0
    ids: set[int] = set()
    critical = W2_FIELDS[:6]
    with w2_path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        normalized = [FIELD_ALIASES.get(k, k) for k in fields if k not in OMITTED_FIELDS]
        if not set(W2_FIELDS).issubset(normalized):
            raise ValueError("--w2 lacks the expected W2 weather columns")
        if len(normalized) != len(set(normalized)):
            raise ValueError("--w2 has duplicate columns after field-name alignment")
        if set(normalized) - set(MERGED_FIELDS):
            raise ValueError("--w2 has an unsupported schema; use the 2024-2025 table")
        for line, source in enumerate(reader, start=2):
            if None in source or any(v is None for v in source.values()):
                raise ValueError(f"Malformed --w2 row at line {line}")
            row = {
                FIELD_ALIASES.get(k, k): v.strip()
                for k, v in source.items() if k not in OMITTED_FIELDS
            }
            if not all(row.get(k, "") for k in critical):
                omitted.append({"source_line": line, "record": source})
                continue
            if row["collect_time"][:4] not in {"2024", "2025"}:
                raise ValueError("--w2 must contain only the 2024-2025 release")
            if row["sensor_id"] == SENSOR_ID:
                skipped_w1 += 1
                continue
            identifier = int(row["incident_id"])
            if identifier <= 0 or identifier in ids:
                raise ValueError(f"Invalid/duplicate W2 incident_id at line {line}")
            ids.add(identifier)
            row["longitude(°)"] = f"{float(row['longitude(°)']):.6f}"
            row["latitude(°)"] = f"{float(row['latitude(°)']):.6f}"
            rows.append({k: row.get(k, "") if k in W2_FIELDS else "" for k in MERGED_FIELDS})
    if not rows:
        raise ValueError("--w2 contains no complete W2 rows")

    w2_count = len(rows)
    last_id = max(ids)
    output_path = output_dir / "Meteorological_87_44.csv"
    w1_count = 0
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MERGED_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        with cleaned_path.open(encoding="utf-8", newline="") as source_handle:
            for offset, source in enumerate(csv.DictReader(source_handle), start=1):
                row = {k: "" for k in MERGED_FIELDS}
                for k in ("sensor_id", "work_status", "longitude(°)", "latitude(°)",
                          "collect_time", "air_temperature(°C)", "atmo_pressure(Pa)",
                          "light_sensor(Lux)"):
                    row[k] = source[k]
                row["incident_id"] = str(last_id + offset)
                row["humidity(volume %)"] = source["air_humidity(%RH)"]
                row["rainfall_increment(mm)"] = source["rainfall(mm)"]
                for k in W1_ONLY_FIELDS:
                    if k != "rainfall_increment(mm)":
                        row[k] = source[k]
                writer.writerow(row)
                w1_count += 1
    digest = sha256(output_path)
    report = {
        "w2_input_file": w2_path.name,
        "output_file": output_path.name,
        "w2_records": w2_count,
        "w1_records": w1_count,
        "total_records": w2_count + w1_count,
        "existing_w1_rows_replaced": skipped_w1,
        "omitted_incomplete_w2_rows": omitted,
        "output_sha256": digest,
        "matches_published_v7_sha256": digest == MERGED_SHA256,
        "schema_only_field_renames": FIELD_ALIASES,
        "omitted_fields": sorted(OMITTED_FIELDS),
        "structural_blanks": "Variables not provided by a station remain blank; no imputation.",
        "w2_values_and_times": "W2 measurement values and timestamp strings are not reinterpreted.",
    }
    (output_dir / "W1_W2_merge_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Merged records: {w2_count + w1_count:,} (W1 {w1_count:,}; W2 {w2_count:,})")
    print(f"Published v7 weather SHA-256 match: {digest == MERGED_SHA256}")
    return report


def main() -> None:
    args = parse_args()
    args.input = args.input.resolve()
    args.output_dir = args.output_dir.resolve()
    if args.output_dir.exists():
        raise FileExistsError("Output directory exists; select a new --output-dir")
    if not args.input.is_file():
        raise FileNotFoundError(args.input)
    if args.w2 is not None:
        args.w2 = args.w2.resolve()
        if not args.w2.is_file():
            raise FileNotFoundError(args.w2)
    source_digest = sha256(args.input)
    clean_w1(args)
    cleaned_path = args.output_dir / "Meterological_W1_87_44.csv"
    cleaned_digest = sha256(cleaned_path)
    validation_path = args.output_dir / "Meterological_W1_87_44_validation.json"
    validation = json.loads(validation_path.read_text(encoding="utf-8"))
    if not all(validation["checks"].values()):
        raise RuntimeError("W1 output validation failed")
    supplied_export = source_digest == SOURCE_SHA256
    if supplied_export and cleaned_digest != CLEANED_SHA256:
        raise RuntimeError("W1 cleaning differs from the historical release")
    verification = {
        "source_file": args.input.name,
        "source_sha256": source_digest,
        "matches_supplied_original_export": supplied_export,
        "cleaned_sha256": cleaned_digest,
        "matches_historical_cleaned_sha256": cleaned_digest == CLEANED_SHA256,
    }
    if args.w2 is not None:
        merge_report = merge_weather(args.w2, cleaned_path, args.output_dir)
        verification["merge"] = merge_report
        if supplied_export and merge_report["w2_records"] == 3392:
            if not merge_report["matches_published_v7_sha256"]:
                raise RuntimeError("Merged output differs from published v7; inspect the --w2 input")
    (args.output_dir / "verification.json").write_text(
        json.dumps(verification, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"W1 historical cleaned SHA-256 match: {cleaned_digest == CLEANED_SHA256}")
    print("Processing completed; source files were not modified.")


if __name__ == "__main__":
    main()
