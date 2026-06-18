# sources/storage-engines/rocksdb/coverage/parse_gcov_output.py

## Purpose
Parses raw gcov text into a compact, human-readable table, optionally restricted to a comma-separated set of interested files.

## Important APIs and Control Flow
`parse_gcov_report` scans stdin for `File '...'` lines followed by `Lines executed:<pct>% of <lines>` lines, building `per_file_coverage` and a final `total_coverage` when no current file is active. `get_option_parser` defines `--interested-files/-i`. `display_file_coverage` computes max filename width, prints header/separator/body, and optionally prints total. `report_coverage` parses args, filters requested files, suppresses totals for filtered reports, and prints a stderr message when no matching coverage exists.

## State, Dependencies, and Risks
The script holds coverage in memory only and writes to stdout/stderr. It depends on gcov output formatting and Python's deprecated `optparse`. Risks include `current_file` not being initialized before unusual input, `max()` failing on empty coverage if not guarded, unordered dictionary output in older Python expectations, and exact regex sensitivity. It is invoked by `coverage_test.sh`.
