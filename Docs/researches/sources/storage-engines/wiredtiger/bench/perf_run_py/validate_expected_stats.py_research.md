# sources/storage-engines/wiredtiger/bench/perf_run_py/validate_expected_stats.py

## Purpose
This CLI validates expected metric values against an Evergreen-style `evergreen_out*.json` performance output file.

## Important APIs, Types, and Functions
`main` parses positional arguments `stat_file`, `comparison_op`, and `expected_stats`, validates filename shape, loads JSON, builds a metric-name/value map, and compares expected values using `eq`, `gt`, or `lt`.

## Control Flow, State, and Dependencies
The script rejects non-matching filenames, decodes the expected-stats JSON object, accumulates errors for missing or mismatched metrics, prints all errors and exits 1 if any exist, otherwise prints success. It depends on the Evergreen output schema used by `perf_run.py` brief mode.

## Integration Points, Risks, and Test Signals
It integrates performance tests with CI threshold checks. Risks include continuing after an invalid comparison operator message without immediate exit and exact equality on potentially noisy numeric metrics. Signals are process exit code and error messages.
