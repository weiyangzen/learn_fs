# Research: sources/storage-engines/foundationdb/tests/python_tests/python_correctness.py

- **Purpose:** Python support or test module `python_correctness.py` in the FoundationDB test tree.
- **Source facts:** 864 lines, 28967 bytes, executable=True.
- **Important APIs/types/functions:** Imports: fdb, fdb.tuple, os, python_tests.PythonTest, random, sys, time, traceback. Classes: KeyValueStore, PythonCorrectness. Top-level functions: get, get_key, get_range, get_range_startswith, set, clear, clear_range, clear_range_startswith, run_test, generate_data, test_callback, test_functions; plus 20 more. Methods: KeyValueStore.get, KeyValueStore.get_key, KeyValueStore.get_range, KeyValueStore.get_range_startswith, KeyValueStore.set, KeyValueStore.clear, KeyValueStore.clear_range, KeyValueStore.clear_range_startswith, PythonCorrectness.run_test, PythonCorrectness.generate_data, PythonCorrectness.test_callback, PythonCorrectness.test_functions; plus 20 more. Constants: none. CLI flags/options observed: none.
- **Control flow:** Executable module: parse command-line arguments, perform setup, run the requested child/test workflow, and convert internal success/failure to process exit status.
- **State and persistence:** creates, reads, renames, or removes filesystem artifacts (1 filesystem call sites)
- **Dependencies:** Python imports: fdb, fdb.tuple, os, python_tests.PythonTest, random, sys, time, traceback.
- **Integration points:** Part of the Python API correctness/performance test area; it integrates with the FoundationDB Python binding and local test clusters.
- **Risks:** Randomized names, ports, or workflow choices make collision avoidance and reproducibility dependent on surrounding seed/control logic.
- **Test signals:** Observable signals include none; failures normally surface as non-zero process exits, failed assertions, missing expected output, or trace severity events.
