<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_coverage_analysis.py -->
# sources/storage-engines/wiredtiger/test/evergreen/code_coverage_analysis.py

Purpose: reads gcovr JSON summary output and prints or writes higher-level coverage metrics, including Atlas-compatible component coverage.

Important APIs: `read_coverage_data()` loads gcovr summary JSON. `read_timing_data()` reads start/end seconds from a two-line file and returns elapsed seconds. `get_branch_coverage()` aggregates branch covered/total counts by component, where component is `filename.split('/')[1]`, inserts overall branch percent, and returns Atlas metric dictionaries. `get_component_coverage()` wraps those metrics under `Test Name: Code Coverage` and writes JSON.

Control flow: `main()` parses summary, outfile, coverage type, timing data, and verbose flag. Default mode prints overall branch coverage and optionally coverage rate per minute. `component_coverage` mode writes the Atlas JSON.

State and persistence: reads `coverage_report/1_coverage_report_summary.json`; optionally writes `atlas_out_code_coverage.json`.

Dependencies and integration: called by `code_coverage_analysis.sh` after gcovr. Depends on gcovr summary fields `branch_percent`, `files`, `filename`, `branch_covered`, and `branch_total`.

Risks and test signals: component extraction assumes paths contain at least two slash-separated parts and nonzero branch totals. Timing file parsing assumes exactly integer seconds. The `outfile` default in `get_branch_coverage` is unused.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_coverage_analysis.py -->
