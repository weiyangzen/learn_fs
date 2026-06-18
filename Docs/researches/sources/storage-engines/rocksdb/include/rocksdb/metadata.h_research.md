# Research: sources/storage-engines/rocksdb/include/rocksdb/metadata.h

## Purpose

`metadata.h` declares public metadata structs describing RocksDB files, live SSTs, blob files, LSM levels, column families, and export/import file sets. These structures support backups, checkpoints, metadata inspection, import, custom compaction decisions, and language bindings.

## Important APIs, Types, and Functions

The header defines `FileStorageInfo`, `LiveFileStorageInfo`, `SstFileMetaData`, `LiveFileMetaData`, `BlobMetaData`, `LevelMetaData`, `GetColumnFamilyMetaDataOptions`, `ColumnFamilyMetaData`, and `ExportImportFilesMetaData`. Fields cover relative filename, directory, file number, file type, size, temperature, checksums, replacement contents, trim-to-size behavior, sequence number bounds, key bounds, sampled reads, compaction state, entry/deletion counts, blob references, creation and ancestor times, epoch number, levels, blob file summaries, and comparator name for import safety.

## Control Flow

DB APIs populate these structs through `GetLiveFilesMetaData`, `GetLiveFilesStorageInfo`, `GetColumnFamilyMetaData`, `GetAllColumnFamilyMetaData`, checkpoint/export flows, and import column-family flows. `GetColumnFamilyMetaDataOptions` filters metadata by optional key range and level. Constructors normalize SST names into `relative_filename` and deprecated leading-slash `name` fields.

## State and Persistence Behavior

The structs are snapshots of persistent DB file state. SST metadata is immutable once produced, while `LiveFileStorageInfo` accounts for mutable live files such as `CURRENT` using `replacement_contents` and `trim_to_size`. Export/import metadata carries enough file and comparator information for `CreateColumnFamiliesWithImport` safety checks. Deprecated fields remain for API compatibility.

## Dependencies and Integration Points

The header depends on `options.h` and `types.h`. Integration points include DB metadata APIs in `db.h`, Java/JNI metadata classes, backup and checkpoint code, BlobDB live-file snapshots, db_stress metadata verification, compact-files examples, sorted run builder, option-change migration, ldb `list_live_files_metadata`, file checksum dump, and import/export tests.

## Risks and Edge Cases

Some fields are optional or zero when unavailable, such as creation time, ancestor time, epoch number, and file checksums. Deprecated `name` and `db_path` must stay consistent with newer `relative_filename` and `directory` for old callers. `BlobMetaData` constructor names appear easy to misuse: it assigns `_file_checksum` to `checksum_method` and `_file_checksum_func_name` to `checksum_value`, so consumers should verify semantics before display. `being_compacted` has had data-race history, so metadata gathering must synchronize with compaction state.

## Test Signals

Signals include Java `RocksDBTest.getColumnFamilyMetaData`, JNI conversions, db_stress `TestGetAllColumnFamilyMetaData`, SST file reader metadata tests, backup engine `LiveFileStorageInfo` tests, BlobDB metadata tests, ldb metadata output tests, and import/checkpoint tests. Assertions should cover level ordering, file counts and sizes, blob summaries, checksum fields, temperature propagation, range/level filtering, and import comparator mismatch rejection.
