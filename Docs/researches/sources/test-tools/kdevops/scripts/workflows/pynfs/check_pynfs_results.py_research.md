# sources/test-tools/kdevops/scripts/workflows/pynfs/check_pynfs_results.py

## Purpose
Compares new pynfs JSON results against a baseline JSON result set and reports newly failing test cases.

## Important APIs and control flow
`main()` loads `sys.argv[1]` as baseline and `sys.argv[2]` as result. It builds a dictionary of failures from `result["testcase"]` keyed by `case["code"]`, removes any failures already present in the baseline, pretty-prints remaining failures, and exits 1 if any remain; otherwise exits 0.

## State and dependencies
Read-only over two JSON files. Uses Python `json`, `sys`, and `pprint`.

## Integration points
Suitable for CI gates where only regressions relative to a known pynfs baseline should fail the run.

## Risks and test signals
There is no argument validation or schema validation; missing files, invalid JSON, missing `testcase`, or missing `code` will raise tracebacks. Test with no new failures, one new failure, existing baseline failures, and malformed input handling if used in CI.
