# Research: sources/storage-engines/tikv/components/test_storage/src/sync_storage.rs

## sources/storage-engines/tikv/components/test_storage/src/sync_storage.rs

Purpose: converts TiKV async `Storage` APIs into blocking test APIs. `SyncTestStorageBuilder<E, F>` builds a `SyncTestStorage<E, F>` from either a default test Rocks engine or a provided engine, optional storage config, and optional GC config. `SyncTestStorage` owns a `Storage<E, MockLockManager, F>` and a `GcWorker<E>`.

Important APIs cover MVCC reads, batch gets, command batch gets, scans/reverse scans, prewrite/commit/cleanup/rollback, lock scanning and resolution, GC, delete range, raw get/put/delete/scan/batch/atomic operations, checksum, and `start_auto_gc`. Async futures are blocked with `block_on`; callback-based commands use `wait_op!`.

Control flow for building storage constructs a `TestStorageBuilder` from engine plus mock lock manager, sets API version, starts a GC worker with a mock region provider, then returns the wrapper. Operation methods mostly pass through context, keys, timestamps, CF names, and options to the underlying storage command.

State and persistence live in the underlying engine and in the started GC worker. `SyncTestStorage` clones the storage and engine handles, while callbacks are synchronous waits. Dependencies include `tikv::storage`, command types, `GcWorker`, raftstore mock region providers, kvproto request types, futures, tracker tokens, and txn types.

Risks include deadlocks or hangs if callback paths fail to invoke `wait_op!`, mock lock manager differences from production, GC worker lifecycle cleanup by drop only, and fixed raw TTL defaults of zero. Test signals are the assertion layer and direct downstream use of blocking return values/errors.
