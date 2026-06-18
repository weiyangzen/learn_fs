# sources/storage-engines/wiredtiger/bench/perf_run_py/perf_config.py

## Purpose
This module holds configuration objects for the WiredTiger Python performance runner.

## Important APIs, Types, and Functions
`TestType` records whether a run is `wtperf` or `workgen` and maps home/test arguments to the proper CLI shape (`-h`/`-O` for wtperf, `--home`/positional for workgen). `PerfConfig` stores executable path, home directory, test path, batch file, extra arguments, requested operations, run count, verbosity, and improved-accuracy flag.

## Control Flow, State, and Dependencies
The module is passive. `PerfConfig.to_value_dict` serializes config fields into report metadata. State is in object attributes. It has no external dependencies beyond Python basics.

## Integration Points, Risks, and Test Signals
It integrates with `perf_run.py` command construction and output reporting. Risks include `TestType.get_home_arg/get_test_arg` returning `None` if both booleans are false, so callers must enforce mutual exclusivity. Signal is correct command lines for wtperf/workgen tests.
