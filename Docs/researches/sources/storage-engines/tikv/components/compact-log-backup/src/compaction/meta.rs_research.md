# sources/storage-engines/tikv/components/compact-log-backup/src/compaction/meta.rs

## Purpose
Builds protobuf metadata for subcompactions and derives migration edits that identify obsolete physical or logical log files after compaction.

## APIs and control flow
`SubcompactionResult::verify_checksum` XORs output SST CRCs and totals output bytes and key counts, comparing them with expected values. `Subcompaction::crc64` hashes input spans and subcompaction identity fields. `to_pb_meta` emits `LogFileSubcompactionMeta`, and `inputs_to_pb` groups spans by physical file. `singleton` and `of_many` create subcompactions from log files for tests and utility paths.

`CompactionRunInfoBuilder` accumulates origin subcompaction spans, updates aggregate compaction timestamps and artifact hash, normalizes spans, scans `StreamMetaStorage`, and writes a `Migration` through `MigrationStorageWrapper`. `expiring` compares compacted spans with each meta file's physical files: fully covered files become deletable physical files; partial coverage becomes `DeleteSpansOfFile`; all-covered metadata can set `destruct_self`; data-only coverage controls `all_data_files_compacted`.

## State, dependencies, and integration
State is a span map keyed by physical file bytes plus a protobuf `LogFileCompaction`. Persistence occurs when `write_migration` writes migration edits to external storage. Dependencies include protobuf BR types, external storage, futures streams, shard config, storage metadata loaders, and compaction structs.

## Risks and test signals
Span normalization is required before deletion derivation; duplicate or unsorted spans could otherwise confuse full-cover checks. `full_covers` asserts compacted span length does not exceed physical file size. Metadata and data files have different deletion semantics. Tests cover partial compaction, full physical-file deletion, whole-meta destruction, multi-meta edits, and aggregate timestamp fields.
