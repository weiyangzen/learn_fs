# sources/storage-engines/rocksdb/db_stress_tool/db_stress_shared_state.h

## Purpose

`db_stress_shared_state.h` defines the shared and per-thread state model for `db_stress`. It provides worker-thread barriers, key-range locking, expected-state accessors, remote compaction queues/results, verification failure flags, background-thread shutdown coordination, and per-thread random/stat/snapshot state.

## Important APIs, Types, and Functions

- `RemoteCompactionQueueItem` packages remote compaction job data and cancellation state.
- `SharedState` exposes mutex/condition variable access, phase counters, start flags, verification failure/stop flags, background-thread counters, and `SafeTerminate()`.
- Key locking APIs include `GetMutexForKey()`, `LockColumnFamily()`, `UnlockColumnFamily()`, and `GetLocksForKeyRange()`.
- Expected-state APIs wrap save/restore, persisted sequence number, prepare/sync operations, existence checks, and CF clearing.
- Remote compaction APIs enqueue/dequeue jobs and add/get/remove results.
- `GenerateNoOverwriteIds()` deterministically chooses no-overwrite keys.
- `ThreadState` stores worker id, per-thread `Random`, `SharedState*`, `Stats`, and snapshot queue.

## Control Flow and State Behavior

`SharedState` is constructed once per DB stress instance and shared by workers and helpers. `db_stress_driver.cc` uses its mutex and condition variable to implement phases: initialization, operation start, operation completion, verification start, verification completion, and background-thread shutdown.

Expected-state methods dispatch to `ExpectedStateManager`. Many write-preparation methods require callers to hold key or range locks. Persisted sequence number access is protected by a dedicated mutex. Key locks are striped by `key >> log2_keys_per_lock_`; range locks are acquired in ascending stripe order through RAII `MutexLock` objects.

Remote compaction uses a mutex-protected FIFO queue and a mutex-protected result map. `ThreadState` seeds workers with repeatable but distinct random streams and tracks held snapshots for later verification/release.

## Dependencies and Integration Points

The header depends on `db_stress_stat.h`, `expected_state.h`, optional `SyncPoint`, gflags declarations, RocksDB `DB`, `Status`, `Snapshot`, compaction service types, port mutex/condition variable primitives, `MutexLock`, and random utilities. It integrates with `db_stress_driver.cc`, `db_stress_test_base.cc`, stress workload implementations, `DbStressListener`, and remote compaction helpers.

## Risks and Edge Cases

Most phase counters and start flags rely on callers holding the shared mutex. Key-lock APIs assume locks were created; they must not be used in `test_batches_snapshots` mode. Whole-column-family locking iterates the truncated stripe count while allocation rounds up partial stripes. Duplicate remote compaction result ids are silently ignored by `emplace`.

Persistent expected-state correctness depends on stable flags and correct pairing of `Prepare*` and `Sync*` calls around DB mutations.

## Test Signals

Signals include all worker phases completing without deadlock, deterministic no-overwrite behavior for fixed seeds, correct crash-recovery verification, no verification failures, remote compaction workers draining jobs and returning results, and final merged stats reporting.
