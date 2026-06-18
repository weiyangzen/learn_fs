# sources/storage-engines/rocksdb/db/external_sst_file_basic_test.cc

## Purpose
`external_sst_file_basic_test.cc` is the broad regression suite for RocksDB external SST creation and ingestion. It validates `SstFileWriter`, `DB::IngestExternalFile`, and `DB::IngestExternalFiles` across normal ingestion, checksum metadata, copy/link behavior, global sequence-number assignment, range tombstones, corruption handling, atomic replacement, file temperature, manifest persistence, snapshot visibility, and column-family concurrency.

The file is not only a unit test for the public external SST APIs. It also pins several internal invariants of `ExternalSstFileIngestionJob`: whether files are copied or linked, when an ingestion must flush memtables, which sequence numbers are assigned, which level receives each file, what metadata survives reopen, and how standalone range deletion files interact with compaction.

## Important APIs, Types, And Functions
The fixture `ExternalSSTFileBasicTest` extends `DBTestBase` and is parameterized by `(write_global_seqno, verify_checksums_before_ingest)`. It creates an external SST directory, probes `RandomRWFile` support, and provides helpers:

- `DeprecatedAddFile` builds legacy ingestion options with global seqno disabled and blocking flush disabled.
- `AddFileWithFileChecksum` exercises the multi-file `IngestExternalFiles` argument path with caller-provided checksums and checksum function names.
- `GenerateAndAddExternalFile` writes point keys, merges, deletions, and range deletions into an external SST, updates an expected map, and ingests the result.
- `VerifyInputFilesInternalStatsForOutputLevel` checks compaction stats for filtered or skipped input files after ingestion-triggered compactions.

`ChecksumVerifyHelper`, `VariousFileChecksumGenerator`, and `VariousFileChecksumGenFactory` model checksum generation, requested checksum function matching, and intentionally varying checksum names. `CompactionJobStatsCheckerForFilteredFiles` observes compaction completion events to verify filtered file counts and skipped bytes.

The main test cases cover basic `SstFileWriter` metadata, aligned buffered writes, CRC32C and custom file checksums, no-copy/move ingestion, global seqno choices for overlapping data, mixed value types, fadvise, sync failures, checksum readahead, range tombstones, corrupted blocks/properties, overlapping input files, standalone range deletion compactions, file temperature, full and partial atomic replacement, bottommost-level constraints, checksum verification after ingest, SST unique IDs, stable snapshots during manifest logging, concurrent column-family drop, and large key/value limits.

## Control Flow
Most tests follow a common pattern: configure `Options`, create one or more external SSTs through `SstFileWriter`, call an ingestion API with a chosen `IngestExternalFileOptions` or `IngestExternalFileArg`, then inspect DB reads, live file metadata, level counts, sequence numbers, filesystem state, or event/stat counters.

The parameterized tests repeatedly call `ChangeOptionsForFileIngestionTest()` so the same ingestion semantics are checked under multiple RocksDB option combinations. They compare `dbfull()->GetLatestSequenceNumber()` to expected increments. Non-overlapping external files can preserve sequence number zero, while files that overwrite DB state, overlap range tombstones, or are ingested while snapshots exist require new global sequence numbers.

Range-deletion tests write tombstone-only or mixed SSTs, then verify inclusive/exclusive boundary behavior, out-of-order tombstone handling, memtable overlap flush decisions, target level placement, and final key visibility. Atomic replacement tests build existing LSM shapes, ingest replacement files with `atomic_replace_range`, and assert rejection for unsupported one-sided ranges, uncovered input files, partial overlap with existing files, memtable overlap when blocking flush is disabled, and snapshot-consistency combinations that are not supported.

Failure tests use `FaultInjectionTestEnv`, `SpecialEnv`, and sync points to disable filesystem syncs, tamper with block checksums, corrupt data/properties blocks, or observe manifest logging. These paths ensure ingestion returns errors when pre-ingest checksum verification is enabled, ignores `SyncFile` not-supported cases where allowed, and cleans up state without exposing partial ingestion.

## State And Persistence Behavior
The tests verify both transient and durable state. Transient state includes the external SST directory, whether source files remain after copy versus move/link ingestion, random-read counters during checksum verification, sync point callbacks, generated expected maps, and parameterized sequence-number expectations.

Persistent state includes table files placed into RocksDB data directories, MANIFEST entries for file checksum, checksum function name, file temperature, unique ID, smallest/largest sequence numbers, and level placement. Reopen checks in `IngestWithTemperature`, `VerifySstUniqueId`, and `StableSnapshotWhileLoggingToManifest` confirm that ingested metadata and sequence advancement survive DB restart.

The suite explicitly checks that `move_files=true` removes the original file only on successful ingestion, failed overlap leaves source files intact, bottommost or atomic replace failures leave existing data unchanged, and full-column-family atomic replacement deletes old files while preserving only newly ingested files. It also validates snapshot isolation while `VersionSet::LogAndApply` writes the manifest: a snapshot taken during manifest logging continues to see the old value, while post-reopen reads see the ingested value and later writes receive higher sequence numbers.

## Dependencies And Integration Points
The file depends on RocksDB test infrastructure (`DBTestBase`, `testharness`, `testutil`, sync points), public APIs (`SstFileWriter`, `IngestExternalFileOptions`, `IngestExternalFileArg`, `ExternalSstFileInfo`, `ColumnFamilyMetaData`, `LiveFileMetaData`), internal metadata (`ColumnFamilyData`, `InternalStats`, `VersionEdit`), environment wrappers (`FaultInjectionTestEnv`, `SpecialEnv`, `FileTemperatureTestFS`), checksum helpers, merge operators, compaction listeners, snapshots, and column-family handles.

It integrates directly with the implementation in `external_sst_file_ingestion_job.cc`: tests assert behavior for file linking/copying and directory sync, random-write global seqno update, checksum generation before and after global seqno mutation, `allow_global_seqno`, `write_global_seqno`, `verify_checksums_before_ingest`, `allow_blocking_flush`, `snapshot_consistency`, `ingest_behind`, `fail_if_not_bottommost_level`, `allow_db_generated_files`-adjacent behavior, file temperature, range conflict registration, and atomic replace deletion edits.

## Risks And Edge Cases
Important covered risks include stale reads after ingestion into universal compaction layouts, bad sequence ordering when files are moved between levels, range tombstone end-key exclusivity, out-of-order range deletions expanding file bounds, incomplete checksum vectors, wrong checksum function names, checksum recomputation after writing global seqno, unsupported random write for seqno patching, sync failure during linked-file ingestion, corruption that is only detected when checksum verification is requested, and file-temperature hints that may be missing or wrong.

Atomic replacement has especially sharp edges. The tests document that one-sided replace ranges are unsupported, upper-bound handling is currently not as exclusive as `DeleteRange` semantics, snapshot consistency with atomic replace is not supported, and partial overlap with existing files is rejected because the implementation does not synthesize tombstone files to split existing SSTs.

The large key/value test is gated by `test::HasBigMem()` because it intentionally approaches 32-bit size limits. Concurrent ingestion and column-family drop is racy by design; the accepted signal is that each operation either ingests and reads the key or fails cleanly without leaving the key visible.

## Test Signals
Primary signals are `ASSERT_OK`/`ASSERT_NOK` status checks, exact `Get` results, `GetLatestSequenceNumber()` deltas, `FilesPerLevel()` and `NumTableFilesAtLevel()` shapes, source-file existence, `LiveFileMetaData` checksum and temperature fields, `ColumnFamilyMetaData` persistence across reopen, compaction event counters, internal compaction stats, sync point callback observations, random-read counts under readahead, and `VerifyChecksum()`.

The executable is registered through the local RocksDB test harness with a `main` that installs the stack trace handler, initializes GoogleTest, registers custom objects, and runs all tests. The parameter instantiation covers all four combinations of writing global seqno and verifying checksums before ingestion.
