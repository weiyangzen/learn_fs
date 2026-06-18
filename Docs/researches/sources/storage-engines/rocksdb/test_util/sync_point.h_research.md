# sources/storage-engines/rocksdb/test_util/sync_point.h

Purpose: declares debug-only sync-point and kill-point test instrumentation macros used to force deterministic thread interleavings and randomized crash testing.

Important APIs/types: `KillPoint` stores crash odds and exclusion prefixes and exposes `TestKillRandom()`. `SyncPoint` declares dependency pairs, dependency/marker loading, callback registration and clearing, processing control, trace clearing, and overloaded `Process()` for string literals. Macros include `TEST_SYNC_POINT`, `TEST_IDX_SYNC_POINT`, `TEST_SYNC_POINT_CALLBACK`, `TEST_KILL_RANDOM`, `IGNORE_STATUS_IF_ERROR`, `testable_assert`, and `ASSERT_TESTABLE_FAILURE`.

Control flow: in debug builds, sync-point macros call the singleton's `Process()`, potentially blocking until dependencies clear and running callbacks. In release builds, most macros compile away to no-ops.

State and dependencies: exposes global testable assertion counter and `TestableAssertionFailure` in debug builds. Depends on RocksDB namespace/slice plus gtest for assertion helpers.

Risks and test signals: tests that depend on sync points must not run under release builds expecting behavior. `ASSERT_TESTABLE_FAILURE` increments/decrements a global counter, so exception paths must not bypass cleanup. Tests should cover macro no-op behavior, indexed point naming, callback arguments, and marker/dependency interaction via the implementation.
