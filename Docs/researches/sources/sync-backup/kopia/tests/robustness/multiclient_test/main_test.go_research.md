<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/multiclient_test/main_test.go -->
# sources/sync-backup/kopia/tests/robustness/multiclient_test/main_test.go

This file is the multiclient test package entry point. `TestMain` parses flags, creates a root client context, initializes a global `TestHarness`, exposes `eng` and `th` for individual tests, runs the suite, logs storage stats before and after cleanup, and exits with the test result.

Control flow ensures harness cleanup runs after `m.Run`, while storage stats are attempted around the lifecycle using `storagestats.LogStorageStats`. The global variables intentionally simplify test functions but couple all tests to one shared harness and repository state.

State persists across tests via shared data and metadata repositories under `repo-path-prefix`. Dependencies are the multiclient framework, robustness engine, and storage stats. Risks include global test order coupling, cleanup errors causing exit status 2, and stats logging failures being fatal around otherwise useful test results. Signals are the multiclient robustness test functions.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/multiclient_test/main_test.go -->
