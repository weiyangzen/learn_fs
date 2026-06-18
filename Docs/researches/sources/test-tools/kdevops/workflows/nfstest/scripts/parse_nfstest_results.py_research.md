# sources/test-tools/kdevops/workflows/nfstest/scripts/parse_nfstest_results.py

## Purpose
Parses kdevops nfstest `.log` output into a normalized JSON result document. The script discovers logs under a results directory, infers suite names, extracts per-test status/assertion/timing information, aggregates suite and overall totals, prints the JSON to stdout, and persists `parsed_results.json` beside the source logs.

## Important APIs, Types, and Functions
The script is a CLI-oriented Python module. `parse_timestamp(timestamp_str)` converts `HH:MM:SS.fraction` strings to seconds, but is currently unused. `parse_test_log(log_path)` is the primary single-file parser and returns a dictionary with `file`, `test_suite`, `tests`, `summary`, `configuration`, and `test_groups`. `parse_all_results(results_dir)` recursively finds `**/*.log`, calls `parse_test_log`, groups outputs by suite key, and builds `overall_summary`. `main()` selects a results directory from argv or `workflows/nfstest/results/last-run`, validates that it exists, emits JSON, and writes `parsed_results.json`.

## Control Flow
`main()` performs input validation, then delegates to `parse_all_results`. `parse_all_results` uses `glob.glob(..., recursive=True)` and sorted iteration for deterministic ordering, chooses a suite key from path segments such as `/interop/` or from the parser's filename inference, appends suite results, and increments aggregate counts/time. `parse_test_log` reads the whole log into memory, scans line by line, builds a `current_test` when it sees `*** `, fills in the name from `TEST: Running test`, records `PASS:` and `FAIL:` assertions, finalizes the test only on a `TIME:` line, parses summary lines matching `N tests (P passed, F failed`, and parses `Total time:` strings in seconds or `XmYs` form.

## State and Persistence Behavior
Parser state is in-memory until `main()` writes `parsed_results.json` to the selected results directory. The emitted JSON contains a generation timestamp from `datetime.now().isoformat()`, so repeated runs are not byte-for-byte stable. `test_groups` is a `defaultdict(list)` while parsing; the standard JSON encoder serializes it as a normal object. Existing `parsed_results.json` is overwritten without backup.

## Dependencies and Integration Points
Depends only on Python standard library modules: `os`, `re`, `sys`, `json`, `glob`, `datetime`, `pathlib`, and `collections.defaultdict`; `Path` is imported but unused. It is invoked by `visualize_nfstest_results.sh` and produces the data expected by downstream visualization tooling, especially `generate_nfstest_html.py` in the same script directory. It assumes nfstest log phrasing such as `OPTS:`, `***`, `TEST: Running test`, `PASS:`, `FAIL:`, `TIME:`, final test summaries, and `Total time:`.

## Risks
Tests without a trailing `TIME:` line are never appended, even if they have pass/fail assertions. A test with multiple assertions is reduced to one final `status`, so mixed pass/fail lines become whatever was seen last before timing. The `TIME:` unit regex `([\d.]+)([ms]?)` cannot distinguish `ms` because the optional group captures one character; millisecond values written as `123ms` are likely parsed as minutes due to the `m` branch. Suite detection uses substring/path checks and can misclassify paths containing suite names incidentally. Configuration parsing only handles narrow `OPTS:` shapes. Files are opened without an explicit encoding or error handling, so malformed logs abort the whole run.

## Test Signals
Useful checks are fixture-driven parser tests for each log suite, logs with missing `TIME:`, failure-only tests, millisecond timing, `Total time` variants, and option lines. Integration tests should run the CLI on a temporary results tree and assert stdout JSON plus `parsed_results.json` contents. The current file has no embedded tests; success is signaled by `visualize_nfstest_results.sh` completing and by downstream HTML generation consuming the JSON.
