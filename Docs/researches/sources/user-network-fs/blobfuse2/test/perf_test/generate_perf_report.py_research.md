<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/perf_test/generate_perf_report.py -->
# sources/user-network-fs/blobfuse2/test/perf_test/generate_perf_report.py

Source path: `sources/user-network-fs/blobfuse2/test/perf_test/generate_perf_report.py`

## Purpose
Compares a current performance JSON report with a base report and emits regression/improvement signals.

## Important APIs, Types, And Functions
Functions: `compare_numbers`. Classes: none declared. Imports: `json`, `argparse`, `sys`, `os`, `math`.

## Control Flow
`argparse` collects current/base/report paths, JSON is loaded, numeric values are compared with `compare_numbers`, and output is printed or written in a report-friendly format.

## State And Persistence
Reads JSON input files and may write a generated comparison report; no durable application state.

## Dependencies And Integration Points
Integrates with Python runtime packages, benchmark datasets, mounted filesystem paths, and JSON/Parquet/report artifacts used by blobfuse2 performance experiments.

## Risks
Comparison quality depends on stable JSON schema and numeric parsing. Threshold logic can hide non-numeric regressions.

## Test Signals
Signals are successful script exit, valid generated JSON/Parquet/report files, timing metrics, and absence of unexpected read/classification/data-generation exceptions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/perf_test/generate_perf_report.py -->
