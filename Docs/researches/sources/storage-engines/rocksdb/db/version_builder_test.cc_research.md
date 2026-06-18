# sources/storage-engines/rocksdb/db/version_builder_test.cc

## Purpose

This file is a focused GoogleTest suite for RocksDB's `VersionBuilder` behavior. It constructs synthetic `VersionStorageInfo` state, applies `VersionEdit` objects, saves the resulting version state, and checks both successful materialization and corruption detection. The covered domain is manifest replay semantics for SST files and blob files: additions, deletions, dynamic-level layouts, blob garbage accounting, SST-to-blob link maintenance, L0 epoch ordering, and estimated active key accounting.

## Important APIs, types, and helpers

- `VersionBuilderTest` owns the test fixture state: `BytewiseComparator`, `InternalKeyComparator`, `Options`, `ImmutableOptions`, `MutableCFOptions`, `VersionStorageInfo`, FIFO options, and level compaction scratch state.
- `Add(...)` allocates a `FileMetaData`, fills key bounds, sequence bounds, file size, entry/deletion stats, `oldest_blob_file_number`, and `epoch_number`, then inserts it into the base `VersionStorageInfo`.
- `AddBlob(...)` creates `SharedBlobFileMetaData` and `BlobFileMetaData` with checksum, linked SSTs, and garbage counters, then inserts it into the base storage.
- `AddDummyFile(...)` and `AddDummyFileToEdit(...)` create small L0 table files used to make blob files reachable from SST metadata.
- `UpdateVersionStorageInfo(...)` runs `PrepareForVersionAppend` and `SetFinalized`, matching the state `VersionBuilder` expects before applying edits.
- `UnrefFilesInVersion(...)` mirrors fixture cleanup by decrementing `FileMetaData::refs` and deleting unreferenced files in temporary versions.

## Control flow and behavior covered

The tests generally follow a common flow: build a base `VersionStorageInfo`, finalize it, create one or more `VersionEdit`s, apply them through `VersionBuilder::Apply`, write to a fresh `VersionStorageInfo` with `SaveTo`, finalize the result, and assert derived state. The early tests validate table-file edits: additions increase level byte totals, deletes remove files, multiple additions are sorted into the saved version, dynamic level bytes do not break accounting, and add/delete combinations for the same file number produce the expected final file location.

The corruption tests verify `VersionBuilder::Apply` rejects deletes at the wrong level, deletes of files absent from the LSM tree, duplicate additions already present in the base version, and duplicate additions already staged by previous edits. Later tests cover blob-file operations: adding blob files, rejecting duplicate blob additions, applying blob garbage to base or newly added blob files, rejecting garbage for missing blob files, and rejecting garbage count/byte overflow.

The larger blob tests exercise `VersionBuilder::SaveTo` behavior. `SaveBlobFilesTo` verifies obsolete blob files are pruned when their linked SSTs disappear or they become entirely garbage. `SaveBlobFilesToConcurrentJobs` captures a concurrency pattern where a lower-numbered blob file can be added after a higher-numbered one already exists. `MaintainLinkedSstsForBlobFiles` checks that SST additions, deletions, trivial moves, and add-then-delete sequences correctly update `BlobFileMetaData::LinkedSsts` without unnecessarily recreating metadata objects.

The final consistency tests validate forced consistency checks: inconsistent SST/blob links, blob files that are entirely garbage but still linked, deleting the same file twice across versions, and invalid L0 ordering by `epoch_number`. `EstimatedActiveKeys` verifies sampled file stats drive the expected active-key estimate, subtracting deletions twice.

## State and persistence behavior

Although this file does not write real MANIFEST records, it models the in-memory result of manifest replay. `VersionEdit` instances represent persistent edit records, while `VersionBuilder` applies them to base `VersionStorageInfo` and emits a new version state. The tests manually manage `FileMetaData` references because temporary versions share metadata pointers with the base version. Blob-file tests are especially stateful: a blob file remains live only when linked SST metadata references it and its garbage counters have not consumed the whole file.

`epoch_number` is treated as required ordering metadata for L0 tests. Files in L0 must be sorted newest-first by epoch, and overlapping files with the same epoch are corruption signals. Tests sometimes pass `EpochNumberRequirement::kMightMissing` to temporary `VersionStorageInfo` to avoid making unrelated metadata mandatory.

## Dependencies and integration points

The suite depends on `db/version_edit.h`, `db/version_set.h`, `VersionStorageInfo`, `VersionBuilder`, `FileMetaData`, `BlobFileMetaData`, `SharedBlobFileMetaData`, internal key formatting, RocksDB test harness macros, and checksum/unique-id constants. It is an integration-level unit test for the version-building layer rather than a pure unit test: it validates interactions among version edits, file metadata, blob metadata, level layout accounting, and consistency checking in `VersionStorageInfo`.

## Risks and edge cases

- Manual reference cleanup is easy to get wrong; missed `UnrefFilesInVersion` calls would leak metadata in tests or hide ownership assumptions.
- Several tests use `kUnknownEpochNumber` for non-L0 additions while newer code may tighten epoch requirements. Future changes must preserve the explicit `EpochNumberRequirement` intent.
- Blob metadata correctness depends on both directions of linkage: SST `oldest_blob_file_number` and blob `LinkedSsts`. The tests show corruption can be detected late at `SaveTo`, not only at `Apply`.
- Some tests intentionally mutate staged/new storage, such as corrupting L0 epoch order, to force consistency failures. These are valuable regression tests for invariants not normally violated by public APIs.

## Test signals

This file is itself the test signal. It exercises success and failure paths with `ASSERT_OK`, `ASSERT_NOK`, `ASSERT_TRUE(s.IsCorruption())`, and state assertions on level bytes, file locations, blob metadata fields, linked SST sets, L0 file ordering, and active-key estimates. Failure messages are checked with `std::strstr`, so user-visible corruption text is part of the tested contract.
