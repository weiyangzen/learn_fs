# sources/sync-backup/rsync/runtests.py

Purpose: Python test runner replacing deprecated `runtests.sh`. It discovers rsync tests, prepares per-test scratch directories, configures environment, runs tests sequentially or in parallel, supports version-mixing/expected-result manifests, and summarizes outcomes.

Important APIs, types, and functions: `parse_args()` defines CLI flags. Helpers include `find_setfacl_nodef()`, `get_tls_args()`, `read_shconfig()`, `get_testuser()`, `prep_scratch()`, `collect_tests()`, `parse_expect_result()`, `outcome_of()`, and `build_rsync_cmd()`. `TestResult` stores result data. `run_one_test()` executes a single test. `main()` orchestrates environment setup, test collection, parallel execution, valgrind log checking, and exit code calculation.

Control flow: `main()` merges CLI and legacy env variables, resolves tool/source dirs and rsync binaries, validates helper programs, builds base env (`RSYNC`, `RSYNC_PEER`, `TLS_ARGS`, `scratchbase`, `PYTHONPATH`, etc.), filters collected `_test.py` files, optionally restricts to expected-result manifest entries, runs tests via `ThreadPoolExecutor` or sequential loop, processes outputs under a print lock, removes scratch dirs for successful/skipped/xfail tests unless preserved, checks valgrind logs, compares skipped/expected outcomes, and exits with a count-like status.

State and persistence behavior: Creates `testtmp` scratch directories, symlinks `src`, writes `test.log`, optional `rsyncd.log`, and valgrind logs. It may delete scratch directories after tests. Runtime state is kept in counters and `outcomes`.

Dependencies and integration points: Depends on Python 3 stdlib, `testsuite/exitcodes.py`, built rsync binaries, helper programs, `shconfig`, `config.h`, and test scripts under `testsuite`.

Risks and test signals: Risks include shell-string `RSYNC` env construction for complex paths, parallel tests sharing external resources, missing helper validation drift, expected-result semantics hiding failures if manifests are wrong, and scratch cleanup permissions. Test by running single, full, parallel, valgrind, expected-result, excluded, and mixed-version suites.
