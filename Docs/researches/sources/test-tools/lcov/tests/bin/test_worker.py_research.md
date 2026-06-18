# sources/test-tools/lcov/tests/bin/test_worker.py

Purpose: worker module for `runtests.py`, executing one test in a subprocess with isolated log and optional coverage environment, then returning a structured result.

Important APIs/types: dataclass `TestResult` mirrors fields used by the runner. Function `run_test_worker(test_name, test_path, log_dir, topdir, coverage_dir, script_args, timeout, coverage_mode, debug=False)` is the ThreadPoolExecutor target.

Control flow and persistence: the worker builds a per-test log path, constructs an environment with `TOPDIR`, `TESTDIR`, `LCOV_HOME`, tool paths, lcov convenience variables, info/count paths, and coverage variables. In coverage mode it creates a per-test coverage subdir and wraps `.pl` with Devel::Cover or `.py` with `coverage run`; shell scripts receive `--coverage`. It runs the command with timeout, writes stdout/stderr and final metadata to the log, measures duration and child RSS via `resource`, and returns `TestResult`.

Dependencies and integration: imported by `runtests.py`; depends on external lcov tool binaries, Python coverage, Perl Devel::Cover, and test scripts honoring common environment conventions.

Risks and test signals: shell scripts receive `--coverage` twice in one branch, which may affect scripts with strict parsing. `result` only distinguishes pass/fail; exit code 2 is not treated as skip unlike legacy `test_run`. Resource usage is process-global for children and can be noisy in threaded execution. Tests should cover pass/fail/timeout, coverage wrapping, and skip semantics.
