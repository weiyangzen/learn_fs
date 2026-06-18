# sources/storage-engines/pebble/internal/manifest/version_edit_test.go

## Purpose
This test file validates manifest version edit serialization, decoding compatibility, virtual backing resolution, blob-reference persistence, edit application, and debug text parsing.

## Important APIs And Tests
- `checkRoundTrip` encodes and decodes a `VersionEdit` and diffs the result.
- `TestVERoundTripAndAccumulate` verifies virtual table backings are restored after decode plus `BulkVersionEdit.Accumulate`.
- `TestVERoundTripBackingValueSizeEqualValueSize` protects a regression where virtual blob reference `BackingValueSize` was lost when equal to `ValueSize`.
- `TestVersionEditRoundTrip` covers complete edits with log numbers, created/removed backings, deleted tables, point/range tables, and range-key kinds.
- `TestVersionEditDecode` uses `testdata/version_edit_decode` to encode/decode hex and quoted binary fixtures.
- `TestVersionEditEncodeLastSeqNum` locks RocksDB-compatible encoding of zero `LastSeqNum` when `ComparerName` is set.
- `TestVersionEditApply` datadriven-applies one or more edits to named versions.
- `TestParseVersionEditDebugRoundTrip` checks text parser/formatter normalization.

## Control Flow
The tests build representative `TableMetadata` objects, initialize physical or virtual backings, serialize edits, decode them, optionally accumulate to repair virtual backing pointers, and compare debug or structural output. The datadriven apply test seeds versions from debug text, splits multiple edits on a sentinel line, accumulates them into one bulk edit, applies them, and updates L0 sublevels.

## State And Persistence Behavior
These tests are directly about persistent MANIFEST behavior. They check binary encodings, decoded nil metadata/backing handling, persistent blob reference values, and compatibility fields that influence recovery.

## Dependencies And Integration Points
The file integrates `VersionEdit`, `BulkVersionEdit`, `TableMetadata`, `BlobFileMetadata`, `L0Organizer`, debug parsers, datadriven fixtures, binary hex fixtures, and `sstable` synthetic prefix/suffix types.

## Risks And Test Signals
The strongest signals cover manifest compatibility and virtual/blob edge cases. Remaining risk is that random map iteration can affect text order for paths not explicitly sorted, although the implementation sorts many debug outputs to stabilize tests.
