# sources/storage-engines/rocksdb/db_stress_tool/db_stress_shared_state.cc

## Purpose

`db_stress_shared_state.cc` implements `SharedState` construction and beginning-verification policy. It wires global stress flags into shared thread coordination state, the expected-state oracle, key-level locking, crash-recovery compatibility checks, and debug-only read-fault sync-point behavior.

## Important APIs, Types, and Functions

- `thread_local bool SharedState::ignore_read_error` stores per-thread read-fault information.
- `SharedState::SharedState(Env*, StressTest*)` initializes counters, flags, atomics, no-overwrite key selection, expected-state manager, key locks, and optional read-fault callbacks.
- `SharedState::ShouldVerifyAtBeginning()` returns true when the stress test has a nonempty expected-values directory.

## Control Flow and State Behavior

The constructor initializes synchronization primitives and counters, seeds `GenerateNoOverwriteIds()` from `FLAGS_seed`, and records the start timestamp. If `expected_values_dir` is nonempty, it checks lock-free atomics and rejects column-family clearing. It then creates either `AnonExpectedStateManager` or `FileExpectedStateManager` and calls `Open()`.

When `FLAGS_test_batches_snapshots` is set, lock creation is skipped. Otherwise the constructor computes lock stripes from `max_key >> log2_keys_per_lock`, rounds up for leftovers, and creates one lock array per column family.

For read or metadata read fault injection in debug builds, it installs a `SyncPoint` callback named `FaultInjectionIgnoreError`; in release mode, read fault injection exits as unsupported.

## Dependencies and Integration Points

The implementation depends on `db_stress_shared_state.h`, `db_stress_test_base.h`, expected-state manager classes, `FLAGS_*` globals, `Env::Default()->NowNanos()`, and `SyncPoint`. `db_stress_driver.cc` uses the constructed state for worker coordination; operations use expected-state and key-lock methods; `DbStressListener` updates persisted sequence number through it.

## Risks and Edge Cases

Lock stripe sizing depends on `log2_keys_per_lock`; impractical values can produce surprising locking behavior. Persistent expected-state mode depends on stable flags across invocations. Constructor failures call `exit(1)`. The `Env*` parameter is unused, so timestamping uses the default environment.

## Test Signals

Good signals are successful expected-state `Open()`, plausible lock creation messages, early crash-recovery verification when expected values are configured, and correct failure on unsupported combinations such as persistent expected state with column-family clearing or release-mode read fault injection.
