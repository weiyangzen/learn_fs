# sources/storage-engines/tikv/tests/integrations/storage/test_storage.rs

## Purpose
This is the broadest TiKV storage integration suite for MVCC transaction semantics and raw KV APIs. It validates reads, writes, deletes, prewrite/commit/rollback/cleanup, forward and reverse scans, lock scanning/resolution, GC, API version validation, raw CF operations, raw atomic APIs, checksums, and concurrent isolation behavior.

## Important APIs, Types, and Functions
Most tests use `AssertionStorage` and `AssertionStorageApiV1` helpers from `test_storage`. Core TiKV APIs include `Mutation`, `Key`, `TimeStamp`, `Context`, `KeyRange`, `ApiVersion`, `dispatch_api_version!`, `checksum_crc64_xor`, `DEFAULT_GC_BATCH_KEYS`, `MAX_TXN_WRITE_SIZE`, and `RESOLVE_LOCK_BATCH_SIZE`. Local helpers include `lock`, `Oracle`, `inc`, `inc_multi`, `backoff`, and benchmark functions.

## Control Flow
Early tests verify MVCC visibility by timestamp for single get, batch get, delete, cleanup, and point-get with primary-key locks. Scan tests build multi-version key layouts and repeatedly check historical snapshots, limits, bounds, reverse bounds, and key-only mode. Lock tests create several prewrites, scan locks by safe point/range/limit, resolve or batch-resolve locks as rollback or commit, and reject illegal TSO ordering. GC tests run both single-engine and raft-cluster storage over small, large, and long-key sets, ensuring old versions disappear after collection. RawKV tests cover get/put/delete/scan, CF selection, key-size errors, API-version rules for V1/V1ttl/V2, raw batch APIs, raw atomic CAS/delete/put, and raw checksum. Isolation tests spawn concurrent increment transactions with retry/backoff and verify every increment observes serializable progress.

## State, Persistence, and Dependencies
State includes MVCC default/write/lock CF entries, raw CF values, locks, rollback records, GC-safe regions, request API version, and in-memory oracle timestamps. Dependencies are the test storage harness, engine traits, kvproto request types, TiKV GC constants, random jitter, and CRC64 checksum logic.

## Integration Points, Risks, and Test Signals
This suite is a primary behavioral contract for transaction storage and raw API validation. Signals are exact visibility assertions, expected errors, lock-info equality, absence after GC, checksum tuple equality, and concurrent punch-card uniqueness. Risks include large stress cases near batch/write-size constants and benchmarks compiled only under bench harness; API-version matrices are dense and should be updated with any key-format change.
