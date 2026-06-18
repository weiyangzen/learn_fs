<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/endian_little.go -->
# sources/storage-engines/pebble/sstable/colblk/endian_little.go

## Purpose
`endian_little.go` defines little-endian implementations of unsafe uint and offset accessors. Because the columnar format stores integers little-endian, little-endian platforms can decode with direct unsafe loads.

## Important APIs, Types, And Functions
The file is selected by little-endian build tags and exports `const BigEndian = false`. It implements `unsafeUint64Decoder.At`, `UnsafeUints.At`, `UnsafeOffsets.At`, and `UnsafeOffsets.At2`.

## Control Flow
`UnsafeUints.At` dispatches on encoded width: 8-byte values are direct `uint64` loads with no base, width 0 returns the column base, widths 4 and 2 load smaller words and add the base, and width 1 reads a byte. `UnsafeOffsets.At` returns direct offset loads. `UnsafeOffsets.At2` loads two adjacent offsets together for width 2 and width 4, then splits the combined word into low and high logical offsets.

## State And Persistence Behavior
The file interprets persisted little-endian integer columns directly in memory. It assumes the block buffer and column payloads are aligned as required by the block and column encoders.

## Dependencies And Integration Points
It is the common implementation on mainstream `amd64`, `arm64`, and other little-endian platforms. Raw bytes, prefix bytes, index block handles, key trailers, and metadata columns all depend on these accessors indirectly through `UnsafeUints` and `UnsafeOffsets`.

## Risks
Unsafe pointer arithmetic and direct typed loads make bounds, alignment, and width correctness essential. The code is duplicated structurally with `endian_big.go`; behavior changes must preserve both variants.

## Test Signals
Most regular CI on little-endian platforms exercises this file indirectly through every columnar block test, plus uint/unsafe-uint tests outside the listed subset. `endian_test.go` covers only byte-reversal helpers.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/endian_little.go -->
