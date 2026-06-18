# sources/storage-engines/rocksdb/utilities/checkpoint/checkpoint_test.cc

## Purpose
This file is the main test suite for RocksDB checkpoint, export, WAL, atomic-flush, and related backup behavior. It verifies that checkpoints and exports are durable, openable, and consistent across column families, blob files, transaction/WAL cases, read-only DBs, and failure-sensitive filesystem scenarios.

## Important APIs, Types, and Functions
`CheckpointTest` is the fixture. It manages DB paths, alternate WAL paths, snapshot/export paths, DB handles, CF handles, and exported metadata. Helper methods open/reopen/destroy DBs, create column families, compact, flush, put/delete/get keys, open read-only DBs, and query table-file counts. `CheckpointTestWithWalParams` parameterizes WAL behavior by log flush threshold, WAL manifest tracking, manual WAL flush, and background inactive WAL close. `CheckpointDestroyTest` parameterizes slow deletion behavior.

Key tests include `GetSnapshotLink`, `CheckpointWithBlob`, `ExportColumnFamilyWithLinks`, `ExportEmptyColumnFamily`, `ExportColumnFamilyNegativeTest`, `CheckpointCF`, `CheckpointCFNoFlush`, `CurrentFileModifiedWhileCheckpointing`, `CurrentFileModifiedWhileCheckpointing2PC`, `CheckpointInvalidDirectoryName`, `CheckpointWithParallelWrites`, `CheckpointWithUnsyncedDataDropped`, read-only and WAL-lock cases, blob-direct-write rejection, `CheckpointWithDbPath`, archived WAL handling, delete-scheduler behavior, atomic flush override tests, mixed atomic/non-atomic flush queue tests, and backup atomic-flush/blob-direct-write tests.

## Control Flow
Most tests create data, take a checkpoint/export, mutate or destroy the original DB, then open the checkpoint/export/backup and verify data or metadata. Race-sensitive tests use `SyncPoint` dependencies and callbacks to pause checkpointing around flushes, manifest rollover, transaction commit, or atomic flush scheduling. Parameterized WAL tests use `FaultInjectionTestFS` to drop unsynced data after checkpoint creation and ensure the checkpoint remains openable.

## State and Persistence Behavior
The fixture creates real RocksDB databases under per-thread test paths plus snapshot, export, backup, and restore directories. Checkpoints are staged and opened as independent DBs. Export tests produce SST copies/links plus `ExportImportFilesMetaData`. Some tests intentionally destroy the original DB, drop unsynced file data, or inspect delete scheduler foreground/background behavior.

## Dependencies and Integration Points
The suite integrates checkpoint implementation, `DBImpl`, backup engine, transaction DB, blob files, column-family metadata, env/file utilities, `FaultInjectionEnv`, `FaultInjectionFS`, `SstFileManager`, delete scheduler, `SyncPoint`, and RocksDB's GoogleTest harness.

## Risks and Edge Cases
The tests cover many timing-sensitive behaviors, so they depend on stable sync-point names and internal sequencing. Some tests are expensive, especially the 2PC loop and backup/restore cases. Several assertions rely on exact status text fragments for blob direct write rejection. Fixture cleanup must destroy CF handles and metadata correctly to avoid leaks. The test name `CheckpointWithArchievedLog` preserves a spelling typo and should not be renamed casually if referenced by scripts.

## Test Signals
A passing suite gives strong confidence that checkpoint directories are openable, contain required blob/WAL/SST metadata, survive unsynced-data loss, reject unsupported layouts, preserve CF data under flush races, honor atomic-flush controls, and interact correctly with backup behavior. Failures usually point to durability, file-lifetime, metadata, or flush/WAL regressions.
