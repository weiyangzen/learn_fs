# Research: sources/storage-engines/foundationdb/tests/python_tests/python_performance.py

- **Purpose:** Python support or test module `python_performance.py` in the FoundationDB test tree.
- **Source facts:** 348 lines, 10398 bytes, executable=True.
- **Important APIs/types/functions:** Imports: argparse, collections.OrderedDict, fdb, fdb.tuple, math, os, python_tests.PythonTest, random, sys, time, traceback. Classes: PythonPerformance. Top-level functions: __init__, run_test, random_key, key, value, insert_data, test_performance, run_future_latency, run_clear, run_clear_range, run_set, run_parallel_get; plus 8 more. Methods: PythonPerformance.__init__, PythonPerformance.run_test, PythonPerformance.random_key, PythonPerformance.key, PythonPerformance.value, PythonPerformance.insert_data, PythonPerformance.test_performance, PythonPerformance.run_future_latency, PythonPerformance.run_clear, PythonPerformance.run_clear_range, PythonPerformance.run_set, PythonPerformance.run_parallel_get; plus 8 more. Constants: none. CLI flags/options observed: --tests-to-run.
- **Control flow:** Executable module: parse command-line arguments, perform setup, run the requested child/test workflow, and convert internal success/failure to process exit status.
- **State and persistence:** creates, reads, renames, or removes filesystem artifacts (1 filesystem call sites)
- **Dependencies:** Python imports: argparse, collections.OrderedDict, fdb, fdb.tuple, math, os, python_tests.PythonTest, random, sys, time, traceback.
- **Integration points:** Part of the Python API correctness/performance test area; it integrates with the FoundationDB Python binding and local test clusters.
- **Risks:** The file uses assertions for contract checks, so optimized Python execution would weaken some validation. Randomized names, ports, or workflow choices make collision avoidance and reproducibility dependent on surrounding seed/control logic.
- **Test signals:** Observable signals include assert; failures normally surface as non-zero process exits, failed assertions, missing expected output, or trace severity events.
