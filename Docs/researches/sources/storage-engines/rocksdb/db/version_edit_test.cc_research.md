# sources/storage-engines/rocksdb/db/version_edit_test.cc

## Purpose

`version_edit_test.cc` is the GoogleTest regression suite for RocksDB's `VersionEdit` manifest-record encoding and decoding. It treats `VersionEdit` as the durable delta format for `Version` state and verifies that edits survive serialization, reject malformed encodings, preserve forward-compatibility rules, and carry newer metadata such as WAL edits, user-defined timestamp persistence flags, blob references, subcompaction progress, and file-open metadata.

The file also tests adjacent `FileMetaData` behavior that feeds manifest records: key-boundary updates, oldest blob-file tracking, memory accounting for string metadata, and the `SubcompactionProgressBuilder` used to reconstruct progress from delta-encoded manifest snapshots.

## Important APIs, Types, and Functions

The central helper is `TestEncodeDecode(const VersionEdit&)`. It encodes an edit with `VersionEdit::EncodeTo(&encoded, 0 /* ts_sz */)`, decodes it with `VersionEdit::DecodeFrom`, re-encodes the parsed edit, and asserts byte-for-byte equality. The helper intentionally disables timestamp stripping by using `ts_sz=0`; the dedicated timestamp-boundary test covers the non-idempotent case where user-defined timestamps are stripped before persistence.

`VersionEditTest` is the main fixture. It exercises `VersionEdit::AddFile`, `DeleteFile`, `SetComparatorName`, `SetPersistUserDefinedTimestamps`, `SetLogNumber`, `SetNextFile`, `SetLastSequence`, `SetColumnFamily`, `AddColumnFamily`, `DropColumnFamily`, `SetMaxColumnFamily`, `SetMinLogNumberToKeep`, `MarkAtomicGroup`, `SetDBId`, `AddBlobFile`, `AddBlobFileGarbage`, `AddWal`, `DeleteWalsBefore`, `SetFullHistoryTsLow`, and `SetSubcompactionProgress`.

The tests depend on manifest tags and custom tags from `db/version_edit.h`: top-level `Tag` values such as `kNewFile4`, `kWalAddition2`, `kWalDeletion2`, `kPersistUserDefinedTimestamps`, and `kSubcompactionProgress`; `NewFileCustomTag` values such as `kPathId`, `kOldestBlobFileNumber`, `kUserDefinedTimestampsPersisted`, and `kFileOpenMetadata`; WAL tags from `db/wal_edit.h`; and subcompaction progress custom tags.

`FileMetaDataTest.UpdateBoundariesBlobIndex` validates `FileMetaData::UpdateBoundaries`. It uses `BlobIndex::EncodeBlob`, `EncodeInlinedTTL`, and `EncodeBlobTTL` to prove only non-inlined, non-TTL blob indexes update `oldest_blob_file_number`, while corrupt or invalid blob indexes return corruption without clobbering existing metadata.

`SubcompactionProgressTest` adds helpers for constructing realistic `FileMetaData`, encoding and decoding `SubcompactionProgress` through `VersionEdit`, verifying decoded file metadata, and checking `SubcompactionProgressBuilder`. It covers both full progress snapshots and delta output-file persistence driven by `SubcompactionProgressPerLevel::UpdateLastPersistedOutputFilesCount()`.

## Control Flow

The first group builds progressively richer `VersionEdit` objects and runs the encode/decode invariant. `EncodeDecode` repeatedly adds files and deletions with large file numbers and sequence numbers, then adds comparator, timestamp persistence, log number, next-file number, and last sequence metadata. `EncodeDecodeNewFile4` focuses on the latest file-add format and checks decoded file flags: marked-for-compaction, path ID, oldest blob file number, and per-file `user_defined_timestamps_persisted`.

`EncodeDecodeNewFile4HandleFileBoundary` is the special timestamp path. It creates internal keys with appended user-defined timestamps, encodes with a nonzero timestamp size, and verifies files whose metadata says timestamps are not persisted have stripped manifest boundaries while files that persist timestamps keep full keys.

Forward-compatibility tests manually inject custom fields through `SyncPoint` callback `VersionEdit::EncodeTo:NewFile4:CustomizeFields`. Unknown safe-to-ignore custom tags are skipped and normal decoded state remains intact. A malformed custom field without a valid tag/length shape returns `ASSERT_NOK`, and unknown custom tags with the non-safe-ignore bit set are rejected.

General manifest-state tests cover empty invalid files, column-family add/drop records, min-log-number retention, atomic groups, safe top-level ignorable tags, and DB IDs. The ignorable-tag tests construct raw varint encodings with `PutVarint32Varint64`, `PutLengthPrefixedSlice`, and safe-ignore mask values to ensure unknown top-level tags either skip an exact payload length or fail on under-length and non-ignorable cases.

Blob-file and WAL tests verify manifest records beyond SST additions. `BlobFileAdditionAndGarbage` adds ten blob files and garbage counters with generated checksum metadata. `AddWalEncodeDecode` adds WAL records with optional synced sizes. The bad-WAL decoding tests prefix manually encoded WAL additions with `kWalAddition2` and a length, then assert corruption messages for missing log number, malformed varint, missing terminate tag, or missing size payload. Debug tests assert exact `DebugString` and `DebugJSON` outputs for WAL additions and deletions.

The subcompaction tests encode progress through a `VersionEdit`, decode it, and compare all major fields. The delta test first persists an initial progress snapshot, advances both levels' last-persisted output-file counts, adds one new file per level, and verifies the next encoded edit contains only the new files. It then feeds initial and delta edits into `SubcompactionProgressBuilder` and checks the accumulated progress has the full file set and latest counters.

The final file-open-metadata tests mutate `VersionEdit::GetMutableNewFiles()` after `AddFile`, set `FileMetaData::file_open_metadata`, and assert `EncodeTo`/`DecodeFrom` preserve it. They also assert the tag value is safe-to-ignore, and `FileMetaData::ApproximateMemoryUsage()` includes the string's heap usage.

## State and Persistence Behavior

`VersionEdit` is persisted to RocksDB MANIFEST files, so this suite is mostly a durable format contract. It protects tag numbers, length-prefixed custom field structure, varint/fixed-width payload expectations, and default elision behavior. File additions require valid smallest/largest keys and a known epoch number; `EncodeEmptyFile` verifies an edit with invalid empty `InternalKey` boundaries is not serialized successfully.

`kNewFile4` persistence includes the level, file number, file size, encoded key boundaries, smallest/largest sequence numbers, and a terminated list of custom fields. Optional fields are written only when they differ from defaults or contain data: nonzero path ID, non-unknown temperature, marked-for-compaction, min-log-number hack, oldest blob file number, unique ID, compensated range-deletion size, tail size, timestamp persistence false, min/max timestamps, and file-open metadata. The tests assert decoded `FileMetaData` reconstructs these choices.

User-defined timestamp persistence is intentionally asymmetric. When `FileMetaData.user_defined_timestamps_persisted` is false and `EncodeTo` receives a nonzero timestamp size, the manifest boundary keys are stripped before writing. Since `DecodeFrom` does not know timestamp size, the round-trip byte invariant is disabled for that scenario and tested separately.

Forward compatibility has two layers. Top-level future tags with `kTagSafeIgnoreMask` set must be followed by a length and can be skipped by older readers; unknown top-level tags without that mask fail. Inside `kNewFile4`, custom tags with `kCustomTagNonSafeIgnoreMask` clear can be skipped after reading their length-prefixed payload, while custom tags with that bit set are critical and cause decode failure if unknown.

WAL additions and deletions are persisted as length-prefixed records under `kWalAddition2` and `kWalDeletion2`, isolating their internal tag streams from the surrounding edit. The tests show the nested WAL decoder requires a log number, known tags, valid sizes, and a terminate tag.

Subcompaction progress is persisted as a length-prefixed `kSubcompactionProgress` field with its own terminated tag stream. Output-file metadata is delta-encoded: after a level marks existing files as persisted, later encodings write only files appended since that count. The builder merges these deltas by appending file metadata and replacing progress counters and next key with the latest edit.

`FileMetaData::UpdateBoundaries` updates smallest/largest internal keys and sequence-number range while also extracting the oldest referenced non-TTL external blob file from blob indexes. It deliberately ignores inlined and TTL blob indexes for oldest-blob-file tracking.

## Dependencies and Integration Points

The suite includes `db/version_edit.h`, `db/blob/blob_index.h`, `rocksdb/advanced_options.h`, `table/unique_id_impl.h`, `test_util/sync_point.h`, `test_util/testharness.h`, `test_util/testutil.h`, `util/coding.h`, and `util/string_util.h`. It uses RocksDB's internal test harness rather than public DB APIs, which keeps tests close to the manifest codec.

The production integration points are `version_edit.cc` and `version_edit.h`, especially `VersionEdit::EncodeTo`, `DecodeFrom`, `EncodeToNewFile4`, `DecodeNewFile4From`, `EncodeFileBoundaries`, `FileMetaData::UpdateBoundaries`, `FileMetaData::ApproximateMemoryUsage`, `SubcompactionProgress::{EncodeTo,DecodeFrom}`, and `SubcompactionProgressBuilder`.

The file is registered as the `version_edit_test` target in RocksDB build metadata (`BUCK`, `CMakeLists.txt`, and `src.mk`). It relies on `SyncPoint` labels in production encoding code to inject future fields and simulate older-reader behavior, so those labels are part of the test coupling.

Blob integration comes through `BlobIndex` and BlobDB metadata constants such as `kInvalidBlobFileNumber`. WAL integration comes through `WalMetadata`, `WalAddition`, `WalDeletion`, `WalAdditionTag`, and the debug serialization support in `wal_edit`. Timestamp integration comes through `InternalKey`, `StripTimestampFromInternalKey`, and `AdvancedColumnFamilyOptions.persist_user_defined_timestamps`.

## Risks and Edge Cases

Manifest compatibility is the primary risk. Changing tag values, field lengths, default elision, or safe-ignore bit semantics can make existing MANIFEST files unreadable or make older binaries accept state they should reject. The tests explicitly cover unknown top-level tags, unknown new-file custom tags, and malformed nested WAL records.

Timestamp boundary handling is subtle because encoding knows timestamp size but decoding does not. A regression can persist timestamp bytes when configured not to, strip bytes when it should not, or make round-trip tests falsely pass by hiding the special case behind `ts_sz=0`.

The `kMinLogNumberToKeepHack` inside `kNewFile4` is a compatibility workaround. Because it is written only once across file additions, changes to edit ordering or file-add encoding can silently alter WAL-retention recovery behavior.

Subcompaction progress merging assumes all edits processed by one `SubcompactionProgressBuilder` belong to the same subcompaction. The tests validate merge mechanics but not cross-subcompaction validation, matching the warning in the header that mixing unrelated progress records can silently corrupt accumulated state.

File-open metadata is intentionally opaque and can be large. Its tag is safe-to-ignore, but current readers preserve it and memory accounting must include it. Future changes to `FileMetaData` string fields need corresponding updates to `ApproximateMemoryUsage()`.

`FileMetaData::UpdateBoundaries` depends on blob-index decoding and sorted key input. Corrupt blob indexes and invalid blob file numbers must fail without rolling back already valid key-boundary state from earlier calls.

## Test Signals

The strongest signal is byte-for-byte encode/decode stability from `TestEncodeDecode` across plain edits, new-file edits, column-family edits, min-log retention, atomic groups, DB IDs, blob-file records, WAL records, and full-history timestamp lows.

Compatibility signals include `ASSERT_OK` for safe ignored top-level and custom fields, `ASSERT_NOK` for undersized ignorable payloads, non-ignorable unknown tags, malformed WAL additions, invalid custom fields, and invalid empty file additions.

Metadata preservation signals include exact checks for marked-for-compaction, path ID, oldest blob file number, `user_defined_timestamps_persisted`, stripped versus retained file boundaries, WAL debug string/JSON output, subcompaction file metadata equality, file-open metadata contents, and approximate memory usage growth.

Regression failures in this target usually indicate a manifest-format or metadata-lifecycle change rather than a pure unit-test expectation issue. Any intentional change should be paired with compatibility reasoning for existing MANIFEST files, older binaries, and recovery paths that replay a sequence of `VersionEdit` records.
