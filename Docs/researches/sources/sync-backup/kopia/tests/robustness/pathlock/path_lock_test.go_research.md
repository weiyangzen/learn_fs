<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/pathlock/path_lock_test.go -->
# sources/sync-backup/kopia/tests/robustness/pathlock/path_lock_test.go

This file validates the path-lock implementation. `TestPathLockBasic` checks same-path blocking, parent/child exclusion, sibling independence, and cleanup after unlock. `TestPathLockWithoutBlock` uses goroutines and `busyCounter` to verify locks do not spin when they should not conflict. `TestPathLockRace` runs randomized concurrent lock/unlock operations.

The tests exercise state transitions in the lock map, unlock behavior, and atomic busy instrumentation. They depend on `os.Getwd`, temporary path construction, `sync.WaitGroup`, and timed goroutine coordination.

Risks tested include deadlock, false conflicts, false non-conflicts, and data races. Residual risk remains around platform-specific path semantics and symlink resolution because tests use lexical paths. These tests are direct signals for concurrency safety in FIO workload mutation.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/pathlock/path_lock_test.go -->
