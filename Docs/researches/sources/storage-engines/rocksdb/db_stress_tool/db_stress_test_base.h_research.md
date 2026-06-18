# sources/storage-engines/rocksdb/db_stress_tool/db_stress_test_base.h

## Purpose

`db_stress_test_base.h` declares the `StressTest` base class and option-initialization helpers used by RocksDB's `db_stress` tool. It defines the shared interface between the generic stress harness and concrete stress-test implementations. The base class owns database lifecycle, common randomized API exercises, transactions, snapshots, backup/checkpoint tests, iterator validation, fault-injection utilities, option mutation, and verification reporting, while subclasses provide the data-model-specific operations.

The header is guarded by `GFLAGS`, matching the flag-driven stress binary. It also includes `rocksdb/io_status.h` before the `GFLAGS` block, then exposes the rest of the declarations only when the stress tool is buildable.

## Important APIs, types, and functions

The public API is intentionally small:

- `StressTest::StressTest()` and virtual destructor construct the test for one DB index/path set.
- Path/env accessors expose DB label/path, expected-values directory, secondaries directory, optional `FaultInjectionTestFS`, and DB env.
- `NewCache()` and `GetBlobCompressionTags()` provide static setup helpers.
- `BuildOptionsTable()`, `InitDb()`, `FinishInitDb()`, `TrackExpectedState()`, `OperateDb()`, `VerifyDb()`, `ContinuouslyVerifyDb()`, `PrintStatistics()`, `EnableAutoCompaction()`, `GetOptions()`, and `CleanUp()` form the main lifecycle and execution surface.
- `MightHaveUnsyncedDataLoss()` centralizes whether expected-state history must account for possible prefix recovery.
- `IsErrorInjectedAndRetryable()` and `IsExpectedTxnError()` classify statuses that should not be treated as ordinary correctness failures.

The protected API is the subclass contract and common operation library:

- Required subclass hooks include `VerifyDb()`, `ContinuouslyVerifyDb()`, `IsStateTracked()`, `TestGet()`, `TestMultiGet()`, `TestGetEntity()`, `TestMultiGetEntity()`, `TestPrefixScan()`, `TestPut()`, `TestDelete()`, `TestDeleteRange()`, and `TestIngestExternalFile()`.
- Optional hooks include `MaybeClearOneColumnFamily()`, `ShouldAcquireMutexOnKey()`, `GenerateColumnFamilies()`, `GenerateKeys()`, `TestKeyMayExist()`, `TestCompactRange()`, `TestPromoteL0()`, `GetControlCfh()`, `TestIterate()`, `TestIterateAttributeGroups()`, `TestIterateAgainstExpected()`, `TestBackupRestore()`, `PrepareOptionsForRestoredDB()`, `TestCheckpoint()`, `TestApproximateSize()`, `TestCustomOperations()`, `RegisterAdditionalListeners()`, and `PrepareTxnDbOptions()`.
- Transaction helpers include `NewTxn()`, `CommitTxn()`, `ExecuteTransaction()`, `ProcessRecoveredPreparedTxns()`, and `ProcessRecoveredPreparedTxnsHelper()`.
- Verification helpers include `AssertSame()`, `GetRangeHash()`, `GetWhiteBoxKeys()`, `VerifyIterator()`, `DumpIteratorDivergenceDiagnostics()`, `ProcessStatus()`, the `VerificationAbort()` overloads, and `DebugString()`.
- Snapshot, property, compaction, WAL/live-file metadata, background-work, and option helpers are declared for use inside the base implementation and subclasses.

The header also declares two enums:

- `LastIterateOp` records the most recent iterator positioning operation so verifier logic can distinguish seek, seek-for-prev, seek-to-first/last, and next/prev behavior.
- `ManifestVerifyMode` records whether reopen should skip MANIFEST checks, warn about reuse/no-write expectations, or enforce strict no-rewrite behavior.

Free functions at the end initialize options from an OPTIONS file or flags, fill general stress defaults, configure user-defined timestamps, and decide whether compaction should be disabled before verification.

## Control flow defined by the interface

The intended flow is: create `StressTest`, call `InitDb()` to open and configure, call `FinishInitDb()` for post-open shared-state work, optionally call `TrackExpectedState()` for history tracing, run worker threads through `OperateDb()`, use `VerifyDb()` or `ContinuouslyVerifyDb()` for correctness checks, print statistics, then `CleanUp()`.

During operation the base class calls subclass hooks at randomized points. Key and column-family generators allow subclasses to expand one random choice into multi-key or multi-CF operations. The base class wraps those hooks with shared read/write options, fault-injection policy, expected-status handling, key locks for range deletes or backup/checkpoint validation, and thread stats.

The transaction helpers are intended to hide pessimistic versus optimistic transaction setup from subclasses. `ExecuteTransaction()` creates a transaction, runs a callback, commits, and retries optimistic `TryAgain` failures within a fixed bound.

## State and persistence behavior

`StressTest` stores both persistent DB-facing state and in-memory test state. Persistent-facing members include paths, env/filesystem wrappers, cache/filter/index factories, `Options`, DB owner/raw pointers, transaction DB pointers, secondary DB handles, column-family handles/names, and MANIFEST file-number/size/current-file state. In-memory test state includes dynamic option mutation tables, reopen counters, preload completion, stopped-state tracking, atomic DB pointer publication, and generated column-family naming.

The header makes persistence expectations visible through helpers such as `MightHaveUnsyncedDataLoss()`, `TrackExpectedState()`, `PreloadDbAndReopenAsReadOnly()`, recovered prepared transaction processing, backup/checkpoint hooks, snapshot acquisition/release checks, and MANIFEST reopen verification methods. It also exposes timestamp helpers that can set older read timestamps for point lookups and range scans when user-defined timestamps are enabled and persisted.

## Dependencies and integration points

The declaration depends on RocksDB core types (`DB`, `Options`, `Status`, `ReadOptions`, `WriteOptions`, `Cache`, `ColumnFamilyHandle`, `Snapshot`, `Transaction`, `TransactionDB`, `OptimisticTransactionDB`, `TransactionDBOptions`), experimental query-filter configuration, user-defined index factories, fault-injection filesystems, and db_stress support types (`SharedState`, `ThreadState`, common flags/helpers, and `CompositeEnvWrapper`). The class is the central bridge between the db_stress driver and concrete test modes such as batched, no-batch, CF-consistency, transaction, wide-column/entity, and custom operation stress tests.

## Risks and sharp edges

- The base class has many virtual hooks with assumptions enforced only by comments, assertions, or surrounding flag logic. Subclasses must update expected state consistently and respect key-locking requirements when they opt into state tracking.
- Several helpers expose raw pointers and manual handle ownership. Column-family and secondary handles are deleted by `CleanUpColumnFamilies()`, so subclasses must not outlive or double-delete them.
- The transaction and timestamp APIs have explicit incompatibilities. For example, user timestamps reject TransactionDB, batched modes, and external ingestion in the implementation.
- Iterator verification is templated and depends on a caller-provided `verify_func`; incorrect hook behavior can make verifier failures hard to diagnose.
- `GetControlCfh()` defaults to the tested column family, but subclasses that use a mirrored/control CF must override it correctly or iterator comparisons will be invalid.
- Fault-injection status classification is strict: injected retryable errors can be ignored in many paths, but data-loss statuses and unexpected transaction errors should surface as failures.

## Test signals

The header exposes the test signals that concrete implementations should use: `ProcessStatus()` for status-to-verification-failure handling, `VerificationAbort()` overloads for detailed failures, `AssertSame()` for snapshot stability, iterator verification and divergence diagnostics, `GetRangeHash()` for compaction non-mutation checks, live-file/property/WAL metadata API probes, backup/checkpoint sampled validation, and `PrintStatistics()`. Subclasses should treat a `SharedState` verification failure or stop request as authoritative and avoid continuing destructive work after it is set.
