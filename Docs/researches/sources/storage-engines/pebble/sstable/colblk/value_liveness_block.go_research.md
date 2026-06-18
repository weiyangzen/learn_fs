# sources/storage-engines/pebble/sstable/colblk/value_liveness_block.go

## Purpose
Implements a columnar reference liveness block used by SSTables with blob references. Each row maps a blob reference ID to encoded value-liveness bytes.

## Important APIs, Types, and Functions
- Constants define a one-column, no-custom-header block layout.
- `ReferenceLivenessBlockEncoder` owns a `RawBytesBuilder` and `BlockEncoder`.
- `Init`, `Reset`, `AddReferenceLiveness`, `Count`, `size`, and `Finish` build the block.
- `ReferenceLivenessBlockDecoder` owns a `RawBytes` column and `BlockDecoder`.
- `Init`, `DebugString`, `Describe`, `BlockDecoder`, and `LivenessAtReference` decode and inspect the block.

## Control Flow
The encoder enforces dense, ordered reference IDs by requiring `referenceID == values.Rows()`. `size` computes the columnar header plus raw bytes column plus one padding byte. `Finish` initializes a version-1 columnar block header and encodes the raw bytes column. The decoder initializes a block decoder and extracts column zero as `RawBytes`.

## State and Persistence Behavior
The persisted block is a normal columnar block with one `DataTypeBytes` column and a final padding byte. Row index equals `base.BlobReferenceID`, so missing IDs cannot be represented sparsely.

## Dependencies and Integration Points
Used by `RawColumnWriter` when writing blob reference index blocks. Layout debugging decodes these values and passes them to blob liveness decoding. Depends on `RawBytesBuilder`, `BlockEncoder`, `BlockDecoder`, `binfmt`, `treeprinter`, and `block.MetadataSize` sizing constraints.

## Risks and Edge Cases
Out-of-order or sparse reference IDs panic. The block metadata size assertion protects reader cache metadata embedding. Empty encoders return a zero-size block but `Finish` still constructs a block if called.

## Test Signals
Covered by `value_liveness_block_test.go`, and indirectly by columnar writer/blob-reference paths.
