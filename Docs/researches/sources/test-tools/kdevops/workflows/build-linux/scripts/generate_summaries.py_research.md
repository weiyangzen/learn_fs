# sources/test-tools/kdevops/workflows/build-linux/scripts/generate_summaries.py

## Purpose
Generates per-host build summary JSON files from raw `build_times` JSON data when collected summaries are missing.

## Important APIs, Types, and Functions
Functions are `generate_summary_from_timing()`, `generate_all_summaries()`, and `main()`. Input entries contain `duration` and `success`; output includes build counts and timing statistics.

## Control Flow
`generate_all_summaries()` finds `*_build_times_*.json`, summarizes each file, writes `<hostname>_summary_<hostname>.json`, and prints counts. Statistics prefer successful builds and fall back to all durations if none succeeded.

## State and Persistence Behavior
Reads raw timing JSON and writes generated summaries beside them.

## Dependencies and Integration Points
Called by `build-linux-visualize` when summaries are absent. Uses Python stdlib and feeds `visualize_results.py`.

## Risks and Edge Cases
The glob does not match direct `build_times_<hostname>.json` output. `build_target` is hard-coded to `vmlinux`, and `make_jobs` is local `os.cpu_count()`, which may not match remote builds.

## Test Signals
Test naming variants, empty timing lists, all-failed builds, mixed success/failure, single successful builds, and missing duration fields.
