# Research: sources/storage-engines/foundationdb/tests/python_tests/ryw_benchmark.py

- **Purpose:** Python support or test module `ryw_benchmark.py` in the FoundationDB test tree.
- **Source facts:** 197 lines, 6375 bytes, executable=True.
- **Important APIs/types/functions:** Imports: argparse, fdb, os, python_tests.PythonTest, sys, time, traceback. Classes: RYWBenchmark. Top-level functions: __init__, run_test, key, get_error, test_performance, insert_data, run_get_single, run_get_many_sequential, run_get_range_basic, run_single_clear_get_range, run_clear_range_get_range, run_interleaved_sets_gets. Methods: RYWBenchmark.__init__, RYWBenchmark.run_test, RYWBenchmark.key, RYWBenchmark.get_error, RYWBenchmark.test_performance, RYWBenchmark.insert_data, RYWBenchmark.run_get_single, RYWBenchmark.run_get_many_sequential, RYWBenchmark.run_get_range_basic, RYWBenchmark.run_single_clear_get_range, RYWBenchmark.run_clear_range_get_range, RYWBenchmark.run_interleaved_sets_gets. Constants: none. CLI flags/options observed: --tests-to-run.
- **Control flow:** Executable module: parse command-line arguments, perform setup, run the requested child/test workflow, and convert internal success/failure to process exit status.
- **State and persistence:** creates, reads, renames, or removes filesystem artifacts (1 filesystem call sites)
- **Dependencies:** Python imports: argparse, fdb, os, python_tests.PythonTest, sys, time, traceback.
- **Integration points:** Part of the Python API correctness/performance test area; it integrates with the FoundationDB Python binding and local test clusters.
- **Risks:** The file uses assertions for contract checks, so optimized Python execution would weaken some validation.
- **Test signals:** Observable signals include assert; failures normally surface as non-zero process exits, failed assertions, missing expected output, or trace severity events.
