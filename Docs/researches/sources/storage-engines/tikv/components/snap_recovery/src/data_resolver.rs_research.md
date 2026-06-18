# sources/storage-engines/tikv/components/snap_recovery/src/data_resolver.rs

Purpose: deletes MVCC data newer than a recovery resolved timestamp and reports progress to BR during snapshot recovery.

Important APIs and types: `DataResolverManager` owns a `RocksEngine`, progress sender, worker join handles, and `resolved_ts`. `LockResolverWorker` deletes all lock CF entries seen by its iterator. `WriteResolverWorker` scans write CF, filters commits above `resolved_ts`, deletes corresponding write and default CF records, and reports batch progress. `Error` wraps invalid argument, not found, engine, and boxed errors.

Control flow: `DataResolverManager::start` spawns separate `cleanup_lock` and `resolve_write` threads. `resolve_lock` creates a lock CF iterator with min-ts hint, deletes every lock, sync-writes the batch, and sends resolved key count. `resolve_write` creates a write CF iterator, loops `batch_resolve_write`, and logs duration. `scan_next_batch` pulls up to `BATCH_SIZE_LIMIT` items, decodes commit ts from the encoded key, and keeps only keys with commit ts greater than the resolved timestamp. `batch_resolve_write` removes each write key and its default CF key built from the write start ts, syncs the write batch, and streams key count/current commit ts.

State and persistence behavior: this code destructively mutates RocksDB CFs `lock`, `write`, and `default` with synchronous writes. The same write batch object is reused across batches, which relies on engine write-batch semantics. Progress is transient over futures mpsc.

Dependencies and integration points: used by `RecoveryService::resolve_kv_data`. Depends on Rocks iterators/write batches, `keys`, `txn_types::{Key, TimeStamp, WriteRef}`, and recoverdata protobuf responses.

Risks: destructive cleanup has no retry/rollback and comments state repeat restore is unsupported. Iterator validity and timestamp decoding must match data-key layout. `cleanup_lock` deletes all lock entries, while write/default cleanup only removes commits above resolved ts. Panics in worker threads propagate through `wait` as `safe_panic!`. Disconnected progress channel stops lock reporting but write cleanup continues after warning.

Test signals: `test_data_resolver` builds a fake engine with write/default/lock records around resolved ts 100, runs manager, and asserts newer writes/defaults and all locks are removed while older records remain.
