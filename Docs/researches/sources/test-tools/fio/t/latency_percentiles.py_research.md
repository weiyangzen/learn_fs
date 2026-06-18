# sources/test-tools/fio/t/latency_percentiles.py

## Purpose
Comprehensive regression harness for fio latency percentile reporting across JSON, JSON+, terse output, unified read/write reporting, sync latency, multi-job aggregation, and per-priority latency summaries.

## Important APIs, Types, and Functions
`FioLatTest` runs fio, parses JSON/terse output, and implements validators: `check_latencies()`, `similar()`, `check_jsonplus()`, `check_sync_lat()`, `check_terse()`, `check_nocmdprio_lat()`, and `check_prio_latencies()`. Test subclasses `Test001` through `Test021` encode direction-specific expectations. `main()` builds a 22-case matrix using null and async engines, percentile option combinations, `fsync`, `numjobs`, `cmdprio_percentage`, `cmdprio_bssplit`, and `unified_rw_reporting`.

## Control Flow
Each test creates an artifact subdirectory, runs fio with latency logs enabled and the configured output format, then parses output. `check_latencies()` reads raw latency log files, filters by data direction or unified reporting, recomputes fio-style percentile ranks, and compares values within the theoretical 1/128 bin error. JSON+ checks validate bins against min/max/sample counts. Terse tests compare selected terse percentile fields to JSON values. Priority tests verify per-priority sample counts, min/max, weighted means, and optionally merged bins.

## State and Persistence Behavior
Artifacts include command, stdout, stderr, exitcode, fio output, workload files, and latency log files under `latency-test-<timestamp>/<test_id>`. No external devices are required, but cmdprio tests are skipped unless running as Linux root. The test list is local to `main()`.

## Dependencies and Integration Points
Depends on fio output schemas, latency log formats, platform async engine selection (`libaio`, `windowsaio`, or `posixaio`), CSV parsing, and Python math/json tools. It validates fio statistic code paths such as `sum_thread_stats()`, JSON+ bins, sync latency accounting, and priority aggregation.

## Risks
Percentile comparisons are approximate and can fail on largest latency bins, as noted by the TODO. Terse index slices are tied to terse version 3 and default percentile layout. Runtime tests can be noisy on slow hosts. Root-only cmdprio skips reduce coverage on common CI setups.

## Test Signals
Passing tests prove expected presence/absence of slat/clat/lat percentiles, consistency with raw latency logs, JSON+ bin self-consistency, terse/JSON agreement, sync latency reporting, multi-job aggregation, unified mixed reporting, and per-priority summary consistency.
