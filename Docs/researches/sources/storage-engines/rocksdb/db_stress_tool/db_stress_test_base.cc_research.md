# sources/storage-engines/rocksdb/db_stress_tool/db_stress_test_base.cc

## Purpose

`db_stress_test_base.cc` implements the non-abstract mechanics behind RocksDB's `db_stress` test harness. It owns the lifecycle of a stress-test database, option construction, DB open/reopen behavior, randomized operation dispatch, transaction helper paths, iterator verification, backup/checkpoint validation, fault-injection handling, and a large set of API probes. Concrete stress-test variants subclass the `StressTest` interface declared in the header and supply data-model-specific operations such as `TestPut`, `TestGet`, `VerifyDb`, and external-file ingestion.

The implementation is compiled only when `GFLAGS` is enabled and is driven almost entirely by global stress-test flags from `db_stress_common.h`. It is not a library component for normal application use; it is a dense integration test driver for exercising RocksDB combinations that are hard to cover with small unit tests.

## Important APIs, types, and helpers

The anonymous namespace provides local scaffolding:

- `StressReadScopedBlockBufferProvider` implements `ReadScopedBlockBufferProvider` with aligned buffers and strict allocation accounting. Its destructor aborts if any read-scoped lease was not cleaned up, making it a leak/lifetime detector for the read path.
- `CreateFilterPolicy()` chooses no filter, Bloom, or Ribbon policy from `FLAGS_bloom_bits` and `FLAGS_bloom_before_level`.
- `OpenFaultInjectionConfig`, `EnableThreadLocalOpenFault()`, `MaybeEnableOpenFaultInjection()`, and `NeedsFaultInjection()` translate open/runtime fault flags into `FaultInjectionTestFS` behavior.

The main `StressTest` implementation covers:

- Construction and cleanup: `StressTest::StressTest()`, `CleanUp()`, `CleanUpColumnFamilies()`, `InitializeListenersForOpen()`, and getters for paths/env/fs.
- Cache and options setup: `NewCache()`, `BuildOptionsTable()`, `InitializeOptionsFromFile()`, `InitializeOptionsFromFlags()`, `InitializeOptionsGeneral()`, `InitializeMergeOperator()`, `CheckAndSetOptionsForUserTimestamp()`, and `ShouldDisableAutoCompactionsBeforeVerifyDb()`.
- DB lifecycle: `InitDb()`, `FinishInitDb()`, `TrackExpectedState()`, `Open()`, `Reopen()`, `PreloadDbAndReopenAsReadOnly()`, `RecordManifestStateBeforeReopen()`, and `VerifyManifestNotRewritten()`.
- Transaction support: `NewTxn()`, `CommitTxn()`, `ExecuteTransaction()`, `ProcessRecoveredPreparedTxns()`, `ProcessRecoveredPreparedTxnsHelper()`, and `IsExpectedTxnError()`.
- Random operation driver: `OperateDb()`, which selects and executes reads, writes, deletes, range deletes, iteration, backup/checkpoint, flush/compaction, WAL, snapshot, property, metadata, and custom operations.
- Verification helpers: `AssertSame()`, `ProcessStatus()`, the `VerificationAbort()` overloads, `DebugString()`, iterator comparison via `TestIterate()`, `TestIterateAttributeGroups()`, `TestIterateImpl()`, `TestMultiScan()`, `VerifyIterator()`, `DumpIteratorDivergenceDiagnostics()`, `GetRangeHash()`, and snapshot release checks.
- API probes: `TestGetLiveFiles*`, `TestGetSortedWalFiles()`, `TestGetCurrentWalFile()`, `TestGetProperty()`, `TestGetPropertiesOfAllTables()`, `TestApproximateSize()`, `TestCompactFiles()`, `TestCompactRange()`, `TestPromoteL0()`, `TestFlush()`, `TestResetStats()`, `TestPauseBackground()`, `TestDisableFileDeletions()`, `TestDisableManualCompaction()`, `TestAbortAndResumeCompactions()`, `TestBackupRestore()`, and `TestCheckpoint()`.

## Control flow

Initialization starts in `InitDb()`: the test prints environment settings, opens the DB, and prepares a table of dynamic option mutations. `FinishInitDb()` then optionally preloads read-only DB contents, restores expected values from a persisted history trace, processes recovered prepared transactions, and wires the compaction filter factory to `SharedState`.

`Open()` is the central lifecycle function. It initializes or loads `Options`, layers the stress-test filesystem and optional fault-injection filesystem into `options_.env`, rebuilds an `SstFileManager` on that env when needed, configures compression managers, validates incompatible flag combinations, discovers or creates column-family descriptors, and opens one of several DB flavors: ordinary `DB`, read-only `DB`, stackable `BlobDB`, `OptimisticTransactionDB`, `TransactionDB`, `DBWithTTL`, and optionally a secondary instance. It also supports fault-injected open retries for non-transaction DBs and verifies that recovered sequence numbers are not behind `SharedState`.

`OperateDb()` is the hot loop. For each reopen epoch, all threads periodically vote for a synchronized `Reopen()`. Within each epoch it sets read/write options from flags, enables thread-local fault injection in debug builds, then repeatedly chooses operations by flag-controlled probabilities. Some maintenance probes are sampled independently before the main read/write/delete/iterate/custom dispatch. User writes may temporarily disable fault injection when unsynced-data-loss tracing cannot yet tolerate missing history entries. Reads branch into `Get`, `MultiGet`, `GetEntity`, or `MultiGetEntity`; iterates branch into `MultiScan`, expected-state iterator verification, normal iterators, or attribute-group iterators.

`Reopen()` cancels background work when needed, releases column-family handles, persists WAL contents before close, optionally calls `Close()`, resets DB owner pointers, records MANIFEST state, calls `Open(..., reopen=true)`, verifies MANIFEST/CURRENT reuse expectations, and restarts history tracing when data-loss-sensitive tracking is enabled.

## State and persistence behavior

The class stores DB identity and paths (`db_index_`, `db_label_`, `db_path_`, expected values path, secondary path), filesystem wrappers (`DbStressFSWrapper`, `FaultInjectionTestFS`, `CompositeEnvWrapper`), option and cache objects, DB owner/raw pointers, transaction DB pointers, column-family handles/names, dynamic option tables, secondary DB state, and MANIFEST verification state.

Persistent state is deliberately stressed rather than abstracted away. `TrackExpectedState()` and `FinishInitDb()` coordinate with `SharedState` history when WAL disabling, manual WAL flushing, or sync-fault injection could cause prefix recovery. `PreloadDbAndReopenAsReadOnly()` writes all keys, commits expected values, flushes, closes, and reopens in read-only mode. `ProcessRecoveredPreparedTxns()` handles prepared transactions left by a prior crash by marking affected expected keys as unknown/pending and randomly committing or rolling back recovered transactions. `TestBackupRestore()` and `TestCheckpoint()` create temporary persistent copies, reopen them with reconstructed options, validate sampled keys against the shared expected state, and clean up directories with fault injection disabled around cleanup.

MANIFEST persistence has explicit test logic. `RecordManifestStateBeforeReopen()` chooses a mode based on `reuse_manifest_on_open`, `optimize_manifest_for_recovery`, best-efforts recovery, fault-injection, DB ID writes, and recovery-flush flags, then records the MANIFEST number/size and `CURRENT` file contents. `VerifyManifestNotRewritten()` warns or exits depending on the strictness mode if the MANIFEST was recreated, grew unexpectedly, or `CURRENT` changed.

## Dependencies and integration points

This file integrates most of the db_stress subsystem: common flags and key/value generators, `SharedState`, `ThreadState`, stress listeners, compaction filters/services, table properties collectors, custom compression managers, filters, wide merge operators, and driver globals such as caches/rate limiters. It exercises public RocksDB APIs (`DB`, `TransactionDB`, `OptimisticTransactionDB`, `BackupEngine`, `Checkpoint`, `DBWithTTL`, `BlobDB`, `Options`, iterators, snapshots, WAL APIs, properties, metadata APIs), internal utilities (`DBImpl`, `InternalStats`, `ParseFileName`, `ReadFileToString`, CRC helpers), and test utilities (`FaultInjectionTestFS`, sync/kill-point support, bytewise timestamp comparator).

The subclass integration surface is important: concrete tests override logical operations and may customize column families, key generation, key-locking policy, additional listeners, transaction DB options, restored DB options, custom operations, and control column-family handles. This base class supplies concurrency, lifecycle, fault, and validation policy around those hooks.

## Risks and sharp edges

- The file is flag-dense; many behaviors rely on global flags being mutually compatible. Several incompatibilities are checked with `exit(1)`, while others rely on assertions.
- DB pointer ownership is delicate. `db_owner_`, `db_`, `txn_db_`, `optimistic_txn_db_`, `db_aptr_`, secondary DB handles, and raw column-family handles must be updated in the right order across open/reopen/cleanup.
- Fault injection is intentionally disabled around some validation and cleanup paths. Missing a disable/reenable region can cause false positives, while over-disabling can hide bugs.
- `Open()` only supports open fault injection on the non-transaction path. Transaction DB paths assert successful open.
- Snapshot and column-family interactions have acknowledged unsafe areas when column families can be dropped concurrently. Some APIs assert `FLAGS_clear_column_family_one_in == 0`.
- Iterator verification must skip undefined combinations involving prefix extractors, bounds, timestamps, and unsupported reverse scans. Incorrect skip logic can either hide a real iterator bug or report a false divergence.
- Backup/checkpoint validation samples limited keys, so it is a signal rather than a full equivalence proof.
- Manifest verification uses the default env to list/read DB files while the DB itself uses `GetDbEnv()`; this is intentional for local DB paths but is a coupling to filesystem assumptions.

## Test signals

The strongest signals are verification failures recorded in `SharedState`, error counters in thread stats, fatal exits/assertions, and stderr diagnostics. Specific test signals include snapshot stability via `AssertSame()`, iterator/control-iterator equivalence, value/wide-column consistency checks, range CRC stability across compaction, restored/checkpoint sampled-key checks, property API availability checks, WAL lock invariants, MANIFEST/CURRENT rewrite warnings or fatal failures, and status processing that treats only injected retryable errors as ignorable. Successful execution with broad flag coverage is itself the intended integration signal.
