# sources/test-tools/fio/mock-tests/tests/test_latency_precision.c

Purpose: isolated regression-style mock test for latency sum precision and long-running average recovery in fio steady-state/stat calculations.

Important APIs/functions: mock `fio_fp64_t` and `clat_stat`; `calc_lat_sum_original`; `calc_lat_sum_improved`; test groups `test_normal_values`, `test_edge_cases`, `test_accumulation_precision`, `test_precision_improvements`, `test_overflow_detection`, `test_long_running_precision`; and `main`.

Control flow: `main` emits a TAP plan for 15 tests, runs each group, and returns `tap_done`. Tests compare original and improved calculations for ordinary values, zero samples, near-overflow safe values, accumulation across mock threads, fractional precision, overflow detection using doubles, and recovering per-second latency after a large sample history.

State/persistence: all state is local mock data; no fio runtime structures or files are used. The long-running test mutates an average using the same incremental mean formula described in comments.

Dependencies/integration: includes math/float/stdint/string and the local TAP helper. It is a focused model of a fio stats concern, not linked against fio proper.

Risks/test signals: some tests assert original and improved values are equal, so they mostly protect refactoring and edge handling rather than proving a behavioral difference. Test 10 always passes after printing direct/cast values. The strongest signal is the long-running per-second latency tolerance.
