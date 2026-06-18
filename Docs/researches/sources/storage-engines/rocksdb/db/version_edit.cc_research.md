# sources/storage-engines/rocksdb/db/version_edit.cc

## Purpose

This file implements the `VersionEdit` manifest codec and related metadata helpers for RocksDB. A `VersionEdit` is the durable unit of version-state change written to MANIFEST: it can carry DB-wide fields, column-family fields, SST additions/deletions, blob-file additions/garbage, WAL additions/deletions, atomic group markers, user-defined timestamp flags, and subcompaction progress snapshots. The implementation defines how those fields are encoded, decoded, debug-rendered, and merged for recovery.

## Important APIs, types, and functions

- `PinnedTableReader` implements copyable pin state for a table reader plus cache handle using acquire/release ordering around the atomic reader pointer.
- `PackFileNumberAndPathId` packs a file number and path ID into one integer, preserving the lower `kFileNumberMask` bits for the file number.
- `FileMetaData::UpdateBoundaries` updates smallest/largest internal keys, sequence bounds, and `oldest_blob_file_number` while scanning entries. It decodes `BlobIndex` values and wide-column blob references to maintain blob dependencies.
- `VersionEdit::EncodeTo` serializes a complete edit using stable manifest tags.
- `VersionEdit::EncodeToNewFile4` and `DecodeNewFile4From` implement the current SST-addition format, including custom tagged metadata fields.
- `VersionEdit::DecodeFrom` parses all supported historical and current tags, including old `kNewFile`, `kNewFile2`, `kNewFile3`, current `kNewFile4`, blob records, WAL records, and safe-ignore future tags.
- `DebugString` and `DebugJSON` render decoded edits for manifest dump tooling.
- `SubcompactionProgressPerLevel`, `SubcompactionProgress`, and `SubcompactionProgressBuilder` encode, decode, and merge compaction progress deltas.

## Control flow

Encoding starts by writing optional scalar fields in a stable order: DB ID, comparator, log numbers, next file number, max column family, min log number to keep, last sequence, compact cursors, and deleted files. New SST files are encoded as `kNewFile4`; the caller must provide timestamp size when there are new files. The encoder rejects invalid file boundaries or missing epoch numbers by returning `false`. Blob additions, blob garbage, WAL additions/deletions, column-family markers, atomic group state, full-history timestamp lower bound, persist-user-defined-timestamp flag, subcompaction progress, and last compacted manifest size follow.

`EncodeToNewFile4` writes level, file number, file size, encoded key bounds, sequence bounds, then a custom-field sequence ending in `kTerminate`. Custom fields include path ID, compaction mark, min-log-number hack, oldest blob file number, oldest ancestor time, creation time, epoch number, checksums, temperature, unique ID, compensated range deletion size, tail size, user-defined timestamp persistence, min/max timestamps, and file-open metadata. File boundaries are stripped of user-defined timestamps when `user_defined_timestamps_persisted` is false.

Decoding loops over varint tags until input is exhausted or malformed. Unknown tags with the safe-ignore mask are skipped by length; unknown unmasked tags produce corruption. Historical file formats populate progressively less metadata, while `kNewFile4` delegates custom-field parsing to `DecodeNewFile4From`. Decode errors are returned as `Status::Corruption` or the status from nested blob/WAL/subcompaction decoders.

Subcompaction progress uses nested tagged custom fields. Per-level progress persists only the delta of output files since `last_persisted_output_files_count_`, preventing quadratic manifest growth as progress is snapshotted repeatedly. The builder merges multiple decoded delta edits by replacing scalar progress fields and appending output-file deltas.

## State and persistence behavior

The file defines durable manifest wire compatibility. Tag numbers are persistent and cannot be changed. Safe-ignore masks allow downgrade/forward compatibility when the reader can skip unknown length-prefixed fields. Critical custom fields without a safe-ignore bit intentionally fail recovery. New SST files added to a `VersionEdit` are also recorded in `files_to_quarantine_` so failed manifest commits can avoid deleting files that may have become durable.

`VersionEdit::ShouldEmitPerColumnFamilyRecoveryEdit` decides whether a recovery edit contains enough state to be worth writing for a column family. `VersionEdit::Clear` resets the object by assigning a fresh default. `AddFile` updates `last_sequence_` to the file's largest sequence number when needed, so file additions advance recovery sequence state.

## Dependencies and integration points

This implementation depends on RocksDB internal coding utilities (`PutVarint*`, `GetVarint*`, length-prefixed slices), internal key encoding, blob index decoding, wide-column serialization, WAL edit codecs, table unique-id helpers, `JSONWriter`, and test sync points. Its output is consumed by manifest readers such as `VersionEditHandler`, `VersionSet`, manifest dump tooling, and best-effort recovery/tailing paths.

## Risks and edge cases

- Manifest wire compatibility is fragile: changing tag values or field encoding would break recovery and downgrade behavior.
- `EncodeTo` requires `ts_sz` for new files and asserts in debug builds; callers must pass timestamp size whenever SST additions are present.
- `DecodeNewFile4From` handles non-safe custom fields strictly. A future critical field will intentionally make older readers fail.
- `PinnedTableReader` copy semantics are explicitly fragile: callers must avoid double releases after copying pinned handles.
- Subcompaction progress merging assumes all processed edits belong to the same subcompaction; the builder does not validate identity and can silently mix unrelated progress.
- The min-log-number-to-keep custom field is described as a compatibility hack embedded inside `kNewFile4`, so it is a known maintenance hazard.

## Test signals

This file contains sync points used by tests around oldest ancestor time, file creation time, unique ID, custom field encoding, and ignored tags. Broader behavior is covered by version-edit, manifest, recovery, and version-builder tests elsewhere. The adjacent `version_builder_test.cc` validates many downstream invariants produced after decoded edits are applied.
