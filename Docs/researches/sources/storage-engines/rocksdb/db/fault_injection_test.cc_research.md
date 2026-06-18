# sources/storage-engines/rocksdb/db/fault_injection_test.cc

## Purpose
`fault_injection_test.cc` verifies RocksDB durability and recovery behavior under simulated data loss. It uses fault-injection environments/filesystems to drop unsynced data, delete unsynced files, reject invalid open patterns, and confirm that synced WAL/compacted data survives crash-like reopen sequences while unsynced data is either absent or does not corrupt reads.

## Important APIs, Types, and Functions
The central fixture is `FaultInjectionTest`, parameterized by key order and option configuration ranges. Important helpers include `CurrentOptions`, `NewDB`, `OpenDB`, `CloseDB`, `Build`, `Verify`, `ReadValue`, `DeleteAllData`, `ResetDBState`, `PartialCompactTestPreFault`, `PartialCompactTestReopenWithFault`, `NoWriteTestReopenWithFault`, and `WaitCompactionFinish`. It uses `FaultInjectionTestEnv`, `FaultInjectionTestFS`, `MockEnv`, `DBImpl::TEST_WaitForCompact`, `WriteBatch::MarkWalTerminationPoint`, `FlushWAL`, `CompactRange`, and `SyncPoint`.

The option enum covers default operation, separate data dir, separate WAL dir, sync WAL, WAL-dir plus sync WAL, and a multi-level stress configuration. `ResetMethod` distinguishes dropping unsynced file data, dropping random unsynced data, deleting files created after the last directory sync, and doing both.

## Control Flow
Each parameterized run opens a DB through `FaultInjectionTestEnv`, writes deterministic keys and 1000-byte pseudo-random values, forces persistence either by WAL sync or compaction depending on the option mode, writes more unsynced data, closes the DB with the filesystem marked inactive, applies a reset method, reopens, and verifies that pre-sync data is found while post-sync data is either found or cleanly not found. The main `FaultTest` loops over random pre/post counts and all relevant option configurations.

Specialized tests cover narrower failure modes. `WriteOptionSyncTest` blocks background flush, rolls the log, writes with `WriteOptions::sync`, flushes WAL without sync, injects loss, and verifies both records survive. `ManualLogSyncTest` validates `FlushWAL(true)` persistence. `UninstalledCompaction` forces a compaction to finish while the filesystem becomes inactive, then verifies reopen ordering and recovery from uninstalled compaction output. `WriteBatchWalTerminationTest` writes a batch with a WAL termination point and confirms only records before the marker survive after simulated loss.

Filesystem contract tests instantiate `FaultInjectionTestFS` directly. `ReadUnsyncedData` reads files that contain synced and unsynced suffixes, optionally syncing, appending, and closing between reads. File-open-contract tests verify `kNoReadersWhileOpenForWrite`, `kNoReopenForWrite`, `SyncFile`, `ReopenWritableFile`, delete/recreate behavior, and expected `IOStatus::NotSupported` cases.

## State and Persistence Behavior
The state under test is the boundary between RocksDB-visible writes and storage-persisted bytes. `FaultInjectionTestEnv` tracks filesystem state as of last sync and can discard later writes or created files. `sync_use_wal_` and `sync_use_compact_` encode which operation is expected to make data persistent for each option configuration. Reopen always calls `env_->ResetState()` before `DB::Open`, simulating a process restart with a possibly damaged storage image. Verification permits unsynced post-fault keys to be missing but treats corruption or unexpected errors as failures.

## Dependencies and Integration Points
This file integrates DB recovery, WAL rolling/sync, flush scheduling, background compaction, directory sync assumptions, file cache behavior, DB options for `wal_dir` and `db_paths`, `MockEnv`, `FaultInjectionTestEnv`, `FaultInjectionTestFS`, `SyncPoint`, and filesystem-level open contracts. It also depends on test utilities for per-thread DB paths, stack trace installation, custom object registration, sleeping background tasks, and deterministic random data.

## Risks
The key risk is overestimating durability: writes protected only by process memory, unsynced WAL bytes, or unsynced table/directory creation must not be required after a crash. Conversely, data that was synced through WAL or made durable through compaction must not disappear. Separate WAL/data directories and multi-level compaction add directory-sync and file-installation risks. The filesystem contract tests guard against readers observing files still open for write and against reopening append paths that the fault-injection model cannot safely track.

## Test Signals
The suite asserts exact value equality for persisted keys, allows only `NotFound` for potentially lost keys, waits for compaction completion, and checks open-contract failures with `IsNotSupported`. It is parameterized for sequential and scrambled key orders and split across option ranges so long-running fault combinations remain bounded. The tests use randomized lengths and resets, making them useful signals for recovery regressions and for bugs in the fault-injection layer itself.
