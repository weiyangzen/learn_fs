# sources/test-tools/lcov/tests/bin/common.py

Purpose: shared Python utilities for the newer Python test runner and worker modules.

Important APIs/types: constants for ANSI colors, `timestamp()`, `detail(key, value)`, `marker()`, `find_topdir()`, `get_parallel_default()`, and class `TestResult`.

Control flow and state: color constants depend on `sys.stdout.isatty()`. `detail` formats fixed-width key/value log lines compatible with shell helpers. `find_topdir` uses `TOPDIR` if valid, otherwise searches upward for either `tests/bin` or `bin` plus `common.mak`. `get_parallel_default` caps multiprocessing CPU count at 8. `TestResult` stores name, result, exit code, duration, memory, log file, coverage directory, and optional error text.

Dependencies and integration: imported by `runtests.py`; a similarly named dataclass exists in `test_worker.py`, so consumers must be clear which class is returned.

Risks and test signals: duplicated `TestResult` definitions can diverge. `detail` truncation math assumes short keys; long keys reduce dot padding. Test signals are successful runner initialization, correctly formatted logs, and topdir discovery from both top-level and subdirectory invocations.
