# sources/storage-engines/wiredtiger/bench/perf_run_py/perf_json_converter_for_atlas_evergreen.py

## Purpose
This utility converts a flat JSON mapping of metric names to values into both Atlas-compatible and Evergreen-compatible performance output JSON files.

## Important APIs, Types, and Functions
Functions are `parse_input_file`, `generate_output_atlas`, `generate_output_evg`, and `main`. CLI options are `--test_name`, `--input_file`, and `--output_path`.

## Control Flow, State, and Dependencies
The script reads the input JSON, builds an Atlas object with `"Test Name"`, `"metrics"`, and `"config"`, builds an Evergreen list containing `info.test_name` and `metrics`, then writes `atlas_out_<test>.json` and `evergreen_out_<test>.json`. State is only the generated files.

## Integration Points, Risks, and Test Signals
It integrates external benchmark metric producers with WiredTiger/Atlas/Evergreen perf consumers. Risks include assuming output directory exists and metric values are JSON-serializable numbers. Signal is two valid JSON files.
