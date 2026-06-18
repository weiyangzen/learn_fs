# sources/test-tools/lcov/tests/bin/runtests.py

Purpose: Python LCOV test driver with serial or parallel execution, replacing shell runner behavior while preserving Makefile compatibility and log/count outputs.

Important APIs/types: CLI parser supports positional tests, `-j/--parallel`, `--coverage`, `--script-args`, `--keep-logs`, `--keep-going`, `--list`, `--timeout`, `--silent`, and `--debug`. Class `TestRunner` implements setup, test discovery, parallel execution, log merge, coverage merge, summary, cleanup, and `run`.

Control flow and persistence: setup creates `test.log.d`, optional `cover_db.d`, initializes `test.log`, and runs `testsuite_init`. Discovery parses `TESTS` variables from Makefiles, recurses into subdirectories, or accepts explicit tests. `run_all_tests` uses `ThreadPoolExecutor` and `test_worker.run_test_worker`. Results are merged into `test.log`, `test.counts` is written, Python coverage files are combined, and `testsuite_exit` is run in cleanup.

Dependencies and integration: called by `common.mak` `check`. Imports `common.py` and `test_worker.py`; runs shell scripts in test directories and lcov tool binaries from the surrounding tree.

Risks and test signals: `--keep-going` is parsed but not used to stop/continue behavior; all submitted tests run regardless. Coverage merge handles Python coverage but only records a note for Devel::Cover. Makefile parsing is simple and may miss complex variables. Test signal is `make check`, with `--list`, `-j`, and coverage modes as focused checks.
