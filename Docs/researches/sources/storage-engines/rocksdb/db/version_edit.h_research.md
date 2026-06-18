# sources/storage-engines/rocksdb/db/version_edit.h

## Purpose

This header declares RocksDB's version-edit data model: the persistent tags used in MANIFEST records, file metadata structures used by versions, subcompaction progress structures, and the `VersionEdit` API for describing changes to DB and column-family state. It is a central contract between manifest writing, manifest replay, version building, table loading, blob tracking, WAL tracking, recovery, and debugging.

## Important APIs and types

- `enum Tag` defines on-disk MANIFEST tags. Values are persistent and include base LevelDB fields, RocksDB-specific file formats, column-family manipulation, atomic groups, blob files, WAL edits, user-defined timestamp fields, subcompaction progress, and last compacted manifest size.
- `enum NewFileCustomTag` defines extensible fields inside `kNewFile4`, including path ID, oldest blob file, time metadata, checksums, temperature, timestamp bounds, unique ID, epoch number, range-deletion compensation, tail size, UDT persistence, and file-open metadata.
- `PinnedTableReader` carries a `TableReader*` and cache handle with concurrency-aware access.
- `FileDescriptor` stores packed file number/path ID, file size, and sequence range, plus optional pinned table reader.
- `FileSampledStats` holds atomic read-sampling counters used for compaction/read statistics.
- `FileMetaData` is the rich in-memory description of an SST: descriptor, key range, stats, sizes, refcount, compaction flags, temperature, blob linkage, time metadata, epoch, checksum, unique ID, tail size, UDT fields, timestamp bounds, and file-open metadata.
- `FdWithKeyRange` and `LevelFilesBrief` provide compact read-path representations of files per level.
- `SubcompactionProgressPerLevel`, `SubcompactionProgress`, and `SubcompactionProgressBuilder` model persisted compaction progress and delta merging.
- `VersionEdit` exposes setters/getters and mutation APIs for manifest edits: file add/delete, blob file add/garbage, WAL add/delete, column family add/drop, compact cursors, full-history timestamp lower bound, atomic group state, and debug output.

## Control flow and API usage

Writers construct a `VersionEdit` by setting DB/CF scalar fields and adding mutation entries. `AddFile` creates or copies `FileMetaData`, appends it with its target level, records the file for quarantine-on-commit-failure, and updates `last_sequence_` from the file's largest sequence number. `DeleteFile` records a level/file-number pair in a set. Blob additions and WAL additions are separate vectors; WAL addition and deletion are asserted to be mutually exclusive at the edit level.

Column-family add/drop operations assert that the edit contains no file/blob/WAL entries and that add/drop are not mixed. Atomic group state is represented by `MarkAtomicGroup` and remaining-entry count. `EncodeTo` and `DecodeFrom` bridge the in-memory edit to the manifest wire format. Debug APIs provide human-readable and JSON dump forms.

`FileMetaData` boundary helpers are used while generating table metadata. `UpdateBoundaries` expects keys in sorted order and updates largest key with each call, while `UpdateBoundariesForRange` accepts unordered range tombstones and compares through `InternalKeyComparator`. Timestamp/time helper methods try local metadata first and fall back to pinned table properties.

## State and persistence behavior

This header is explicit about persistent compatibility. Tag values are written to disk and must remain stable. Safe-ignore masks separate forward-compatible unknown fields from critical fields. `kFileNumberMask` reserves high bits for path ID packing. Unknown time and epoch constants are represented as zero, while `kReservedEpochNumberForFileIngestedBehind` reserves epoch one for ingest-behind behavior.

`FileMetaData` owns mutable recovery and compaction state that survives through version building: refcounts, `being_compacted`, `marked_for_compaction`, stats initialization, blob references, checksums, user-defined timestamp persistence, and file-open metadata. `ApproximateMemoryUsage` must be updated when new string fields are added, which is noted as a maintenance warning.

Subcompaction progress deliberately persists output-file deltas rather than the full accumulated output list every time. The builder reconstructs complete progress from a sequence of edits, but its comments state that callers must ensure all inputs refer to the same subcompaction.

## Dependencies and integration points

The header depends on blob addition/garbage records, DB internal format, WAL edit definitions, arena and malloc utilities, advanced cache/options APIs, table readers, unique-id helpers, and sync points. It is included by `version_edit.cc`, `version_edit_handler`, `version_builder`, `version_set`, manifest dump utilities, recovery code, tests, and blob/compaction components that need file metadata.

## Risks and edge cases

- `PinnedTableReader` is copyable but not movable; copy assignment relies on caller discipline around cache-handle lifetime.
- Many fields have persistence defaults. Missing or incorrectly defaulted fields, especially epoch number, timestamp persistence, or checksum fields, can cause recovery errors or subtle metadata loss.
- `FileMetaData::UpdateBoundaries` requires sorted keys; misuse would corrupt smallest/largest bounds.
- `FileMetaData::ApproximateMemoryUsage` is manually maintained for string fields.
- `VersionEdit::IsWalManipulation` and edit-entry counts rely on booleans and vector sizes; mixed WAL/file edits are constrained by assertions but still require disciplined callers.
- Subcompaction progress builder can silently merge unrelated subcompactions.

## Test signals

The header exposes test-only hooks such as `PinnedTableReader::TEST_SetReader` and `SubcompactionProgressPerLevel::TEST_ClearOutputFiles`, plus sync points in constructors and tail-size calculation. Its behavior is indirectly exercised by version-edit codec tests, manifest recovery tests, and `version_builder_test.cc`.
