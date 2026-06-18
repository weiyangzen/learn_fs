# sources/storage-engines/tikv/src/server/reset_to_version.rs

Purpose: implements a RocksEngine debug/admin reset-to-version operation. It removes write/default MVCC records newer than a target timestamp and then removes all lock-CF records.

Important APIs/types/functions: `ResetToVersionState`; `ResetToVersionWorker`; `ResetToVersionManager`; `process_next_batch`; `process_next_batch_lock`; `start`; `state`; `wait`.

Control flow: worker construction seeks write and lock iterators and marks `RemovingWrite`. Write scanning parses each `WriteRef`, decodes commit_ts from the encoded key, selects writes with commit_ts greater than the target, deletes the write-CF entry and matching default-CF entry based on `write.start_ts`, and flushes batches of 256. The manager thread then switches to `RemovingLock`, deletes all lock-CF keys in batches, and marks `Done`.

State/persistence: direct RocksDB write batches mutate `CF_WRITE`, `CF_DEFAULT`, and `CF_LOCK`; this bypasses raft consensus. Shared state records progress counts. Drop joins the worker thread.

Dependencies/integration: invoked by debug tooling via debugger reset. Depends on Rocks iterators/write batches, MVCC key encoding, `txn_types`, and TiKV thread-group propagation. Risks include many unwraps/expect panics on engine errors, broad lock deletion, no cancellation, Rocks-only implementation, and TODO around disabling WAL for v2. Unit test verifies newer writes/defaults and all locks are removed.
