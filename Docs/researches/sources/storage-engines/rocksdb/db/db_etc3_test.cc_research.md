# sources/storage-engines/rocksdb/db/db_etc3_test.cc

## Purpose

`db_etc3_test.cc` is a focused GoogleTest file for RocksDB MANIFEST rollover and MANIFEST-size auto-tuning behavior. It exercises DB reopen, flush, column-family create/drop, external SST ingestion, imported column-family creation, and physical file deletion by range as different classes of manifest-writing operations. The tests are less about key/value semantics and more about whether MANIFEST rotation thresholds, persisted compacted-manifest size, and foreground/background manifest-write classification remain correct.

## Important APIs, Types, and Functions

- `DBEtc3Test` derives from `DBTestBase` with fsync enabled for realistic metadata persistence.
- `ManifestRollOver` configures `max_manifest_file_size=0` and `max_manifest_space_amp_pct=0` to force a new MANIFEST on each manifest write.
- `AutoTuneManifestSize` is the main scenario test. It uses `DBOptions::max_manifest_space_amp_pct`, dynamic `SetDBOptions`, `CreateColumnFamily`, `DropColumnFamily`, `DestroyColumnFamilyHandle`, `SetOptions`, `IngestExternalFile`, `CreateColumnFamilyWithImport`, and `DeleteFilesInRanges`.
- The test builds external SSTs with `SstFileWriter` and import metadata with `LiveFileMetaData` and `ExportImportFilesMetaData`.
- It uses `dbfull()->TEST_Current_Manifest_FileNo()` as the primary internal signal for whether a write rotated the MANIFEST.

## Control Flow

`ManifestRollOver` repeatedly opens with an extra column family, writes and flushes data, verifies the flush caused a manifest file number increase, reopens with the same CF set, and verifies reopen also creates a new manifest while preserving values.

`AutoTuneManifestSize` is split into phases. Phase 1 validates that foreground manifest writes receive bounded extra headroom: several large CF-name creates fit under the relaxed threshold, then the fifth rotates. Phase 2 disables auto-tuning and shows a reduced `max_manifest_file_size` causes frequent rotation. Phase 3 enables `max_manifest_space_amp_pct`, verifies the tuned threshold allows additional manifest growth, and checks dynamic option changes recompute from the last compacted MANIFEST size. Phase 4 distinguishes foreground manifest writes from background flush writes using CF operations, `SetOptions`, external SST ingestion, imported CF creation, and `DeleteFilesInRanges`; each foreground operation should stay on the current MANIFEST until a background flush rotates it. Phase 5 closes and reopens with `reuse_manifest_on_open=true`, then verifies the persisted compacted size prevents immediate rotation of a reused large MANIFEST.

## State and Persistence Behavior

The persistent state under test is the MANIFEST file number, the compacted MANIFEST size used for auto-tuning, the set of live column-family definitions, imported/ingested file metadata, and key/value data after reopen. The test intentionally keeps many CF handles alive until the persisted-size phase, then collects names and destroys handles before `Close()` so reopen can validate reused manifest metadata. A failure in persisted compacted-size loading would show up as an unexpected manifest number change on reopen or on early post-reopen CF creation.

## Dependencies and Integration Points

This test integrates `DBTestBase`, `DBImpl` test hooks, public DB option mutation APIs, CF management APIs, external SST ingestion, column-family import metadata, file-range deletion convenience APIs, `SstFileWriter`, `rocksdb/metadata.h`, and manifest rewrite/rotation logic inside `VersionSet::LogAndApply`.

## Risks and Edge Cases

The most important risk covered is misclassifying foreground manifest writes as background writes, or giving foreground writes unbounded headroom. Either bug can cause excessive MANIFEST growth or excessive rotation. The persisted-size phase covers a subtle restart risk: if `reuse_manifest_on_open` loses the compacted-size baseline, the DB may rotate a manifest immediately and defeat reuse. The test also depends on CF-name payload sizes to make threshold crossings deterministic, so future MANIFEST encoding changes can require threshold adjustment.

## Test Signals

The test asserts manifest file-number changes, successful point reads after flush/reopen, successful ingestion/import/delete range operations, dynamic option effects, and exact CF handle counts. It is a regression signal for MANIFEST rollover, auto-tuned manifest thresholds, foreground/background manifest write policy, and persistence of the compacted-size baseline.
