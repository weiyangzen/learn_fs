<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/endian_big.go -->
# sources/storage-engines/pebble/sstable/colblk/endian_big.go

## Purpose
`endian_big.go` defines big-endian implementations of unsafe uint and offset accessors. Its goal is to keep columnar block integer decoding semantically little-endian even on big-endian CPUs.

## Important APIs, Types, And Functions
The file is guarded by big-endian build tags. It exports `const BigEndian = true` and implements `unsafeUint64Decoder.At`, `UnsafeUints.At`, `UnsafeOffsets.At`, and `UnsafeOffsets.At2`. Multi-byte values are loaded through unsafe pointer arithmetic and passed through `bits.ReverseBytes16/32/64` as needed.

## Control Flow
`UnsafeUints.At` is optimized by encoded width. Width 8 loads and reverses a raw `uint64` with no base. Width 0 returns the base. Widths 4 and 2 reverse a loaded word and add the base. Width 1 reads a byte and adds the base. `UnsafeOffsets.At` and `At2` perform similar dispatch for 0-, 1-, 2-, and 4-byte offsets, with `At2` loading adjacent offsets together when possible.

## State And Persistence Behavior
The persistent representation remains little-endian and width-coded. This file only changes in-memory interpretation on big-endian targets. It relies on block buffers being aligned according to the column encoders' alignment rules.

## Dependencies And Integration Points
It integrates with `UnsafeUints`, `UnsafeOffsets`, and `unsafeUint64Decoder` defined in the uint encoding files outside this work item. It is selected instead of `endian_little.go` by Go build constraints.

## Risks
The code is performance-sensitive and unsafe. `At2` has subtle byte-order handling, especially for 1-byte offsets where no `ReverseBytes16` is required because the function returns the values in logical order. Mistakes would silently corrupt offsets, which would affect raw bytes, prefix bytes, and many higher-level block decoders.

## Test Signals
Direct accessor tests likely live in `uints_test.go` and `unsafe_uints_test.go`, outside this subset. `endian_test.go` covers the shared reversal helpers, not this build-tagged file on little-endian CI.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/endian_big.go -->
