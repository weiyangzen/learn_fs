## sources/storage-engines/rocksdb/db_stress_tool/no_batched_ops_stress.cc

### Purpose

`no_batched_ops_stress.cc` implements the `NonBatchedOpsStressTest` variant of RocksDB's db_stress tool. It exercises individual point, range, iterator, entity/wide-column, transaction, WBWI ingestion, external-file ingestion, secondary-DB, and timestamped operations while maintaining an explicit `SharedState` expected-value model. The class is compiled only under `GFLAGS` and is constructed through `CreateNonBatchedOpsStressTest()`.

### Important APIs, Types, And Functions

- `NonBatchedOpsStressTest` derives from `StressTest` and overrides the non-batched operation surface.
- `VerifyDb()` performs full partitioned validation using iterator, `Get`, `GetEntity`, `MultiGet`, `MultiGetEntity`, and `GetMergeOperands` modes.
- `ContinuouslyVerifyDb()` optionally tails a secondary DB and samples iterator/Get behavior under a checksum pass.
- `MaybeClearOneColumnFamily()` drops and recreates non-default column families while updating shared expected state.
- `TestKeyMayExist()`, `TestGet()`, `TestMultiGet()`, `TestGetEntity()`, and `TestMultiGetEntity()` validate point-read APIs, timestamp reads, error injection, and transaction read-your-own-write behavior.
- `TestPrefixScan()` and `TestIterateAgainstExpected()` stress prefix and general iterator correctness, including upper bounds, prefix mode, multi-CF coalescing iterators, lazy value preparation, refresh, and backward scans.
- `TestPut()`, `TestDelete()`, and `TestDeleteRange()` apply writes and commit or roll back `PendingExpectedValue` records around actual DB status.
- `TestIngestExternalFile()` builds SST files with `SstFileWriter`, optionally standalone range-delete files, then tests direct ingest and prepare/commit/abort ingestion flows.
- `VerifyOrSyncValue()` and `VerifyValueRange()` are the core expected-state validators for primary and eventually consistent secondary/follower reads.
- `PrepareTxnDbOptions()` installs rollback-deletion callback semantics for no-overwrite keys, and `MaybeAddKeyToTxnForRYW()` injects uncommitted operations into transactions for read-your-own-write checks.

### Control Flow

The class acquires per-key or range locks before mutating expected state because `ShouldAcquireMutexOnKey()` returns true and every write path has a corresponding `Prepare*()`/`Commit()`/`Rollback()` action. Write operations retry injected retryable failures when the initial WAL write might have succeeded; once recovery catches up, expected state is committed only if the DB write ultimately reports success. Non-retryable unexpected statuses usually set verification failure or call `SafeTerminate()`.

Validation reads intentionally capture expected state before and after DB calls. For concurrent primary reads, values are accepted only when the returned value base lies in the pre/post expected range and the key existence result is consistent. Secondary verification takes an even wider window: it records lower-bound expected values before `TryCatchUpWithPrimary()`, optionally flushes memtables or WALs when WAL visibility would otherwise be unavailable, then checks secondary results against lower and upper expected bounds.

Iterator verification first snapshots expected state for a `[lb, ub)` range, creates either a normal or coalescing iterator, and then performs full forward and backward passes to detect skipped or out-of-order keys. It may refresh the iterator after SuperVersion changes, then runs random `Seek`, `SeekForPrev`, `Next`, and `Prev` movement. Failures dump expected-state fields, read options, iterator properties, and replay comparisons using standard/trie and direct/coalescing iterators.

External ingestion creates temporary SST files under the DB path using a thread-specific hidden filename, locks the target range, prepares expected values, writes keys or a standalone range-deletion file, and then ingests with randomized `IngestExternalFileOptions`. Prepare/commit mode can be split per file, committed as handles, explicitly aborted, or rolled back by handle destruction, and expected state follows the final ingest outcome.

### State And Persistence Behavior

The durable effects are ordinary RocksDB writes, merges, deletes, range deletes, WAL records, ingested SST files, and optionally timestamped versions and wide-column entities. The separate expected-state model is in `SharedState`, where every key/CF records value base, delete counters, pending writes, and pending deletes. This file does not persist that model directly; it uses it as a live correctness oracle for the DB under stress.

The stress test also interacts with secondary DB state through `secondary_db_` and `secondary_cfhs_`, transaction state through `TransactionDB`, injected filesystem errors via `db_fault_injection_fs_`, and stats counters in `ThreadState::stats`. Error-injection paths deliberately disable faults during diagnostic or verification reads so failures are attributed to the operation under test rather than the checker.

### Dependencies And Integration Points

This file depends on `db_stress_common.h`, `db_stress_shared_state.h`, `expected_state.h`, `db_stress_listener.h`, `db/dbformat.h`, wide-column helpers, `TransactionDB`, `SstFileWriter`, `WriteBatchWithIndex`, and `FaultInjectionFileSystem`. It integrates with a large flag surface such as `FLAGS_use_txn`, `FLAGS_user_timestamp_size`, `FLAGS_use_merge`, `FLAGS_use_put_entity_one_in`, `FLAGS_use_multi_cf_iterator`, `FLAGS_use_sqfc_for_range_queries`, `FLAGS_disable_wal`, and external ingestion flags.

### Risks And Edge Cases

- Expected-state synchronization is subtle when retryable injected errors occur after a WAL append but before the original operation returns success. Incorrect `initial_wal_write_may_succeed` handling would either mask a lost write or falsely accuse recovery.
- Timestamped reads intentionally skip some exact checks for older timestamps because the shared model only tracks latest state. Coverage depends on careful `read_older_ts` handling.
- `TestMultiGet()` appears to disable read/metadata error injection at the end of one verification helper where the surrounding comment says to enable it back. If that is not compensated by higher-level control flow, later fault-injection coverage could be weakened.
- Iterator checks assume db_stress key encodings can be parsed by `GetIntVal()` and set an upper bound to avoid batched-op keys when the DB is not freshly destroyed.
- Standalone range-delete ingestion requires a continuous overwrite-allowed key range; otherwise the operation returns early, so coverage can be sparse under high no-overwrite rates.
- Secondary verification accepts value ranges rather than exact values, which is appropriate for lagging secondaries but can hide ordering bugs that still fall within the accepted expected-value interval.
- Wide-column verification is central to `GetEntity`, `MultiGetEntity`, iterators, and ingestion; any mismatch between default-column value and generated wide-column set causes hard verification failure.

### Test Signals

This file is itself a stress-test implementation. Useful signals are db_stress runs across transaction policies, timestamp sizes, wide columns, blob/direct-write modes, WBWI ingest, prefix/table-filter range reads, manual WAL flush, disabled WAL secondary verification, and fault-injection severity levels. Static research only; no build or stress command was run for this report.
