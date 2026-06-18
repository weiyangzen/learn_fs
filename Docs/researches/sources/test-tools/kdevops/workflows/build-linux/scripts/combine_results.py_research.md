# sources/test-tools/kdevops/workflows/build-linux/scripts/combine_results.py

## Purpose
Combines per-host build-linux summary JSON files into `combined_report.json` with host details, totals, and approximate aggregate statistics.

## Important APIs, Types, and Functions
Functions are `combine_results(results_dir)` and `main()`. It expects `*_summary_*.json` files with host counts and timing statistics.

## Control Flow
The script loads all summary files, accumulates total/success/failure counts and total hours, approximates aggregate durations by repeating host averages, writes `combined_report.json`, and prints a summary.

## State and Persistence Behavior
Reads summaries and writes one combined JSON report in the results directory.

## Dependencies and Integration Points
Uses Python stdlib. Integrates with summaries from `build_linux.py` or `generate_summaries.py` and downstream reporting/manual inspection.

## Risks and Edge Cases
The glob does not match direct `summary_<hostname>.json` output from `build_linux.py`. Aggregate stats are approximate rather than raw-duration based. Missing keys raise exceptions.

## Test Signals
Test no summaries, direct and collected naming patterns, all-failed summaries, unequal host counts, and malformed summary JSON.
