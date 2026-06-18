# sources/storage-engines/pebble/sstable/tablefilters/binaryfuse/bitpacking/bitpacking.go

## Purpose
Implements compact random-access encodings for binary fuse fingerprints with 4, 8, 10, 12, and 16 bits per value. The package optimizes for fast decoding of individual or triple fingerprint positions without materializing an unpacked slice.

## Important APIs, Types, And Functions
`SupportedBitsPerValue` lists valid widths. `EncodedSize` computes exact output sizes including padding needed for unsafe reads. `Encode8` handles 4- and 8-bit values; `Encode16` handles 10-, 12-, and 16-bit values. Helpers include `encode4bpv`, `encode10bpv`, `encode12bpv`, `encode16bpv`, `Decode`, `Decode3`, and unsafe little-endian readers.

## Control Flow
Encoding switches on bits-per-value and uses specialized packing loops: SWAR nibble packing for 4 bits, direct copy for 8/16 bits on little-endian systems, 32-value groups for 10 bits, and 2-value/8-value groups for 12 bits. Decoding computes byte offsets and shifts for the selected width. `Decode3` performs one max-index bounds check and returns three values for binary fuse probes.

## State And Persistence Behavior
The functions are pure transformations over caller-owned buffers. The encoded bytes are persisted inside binary fuse SSTable filter blocks, with padding bytes included to support safe unaligned reads.

## Dependencies And Integration Points
Depends on `encoding/binary`, `unsafe`, CockroachDB errors, and invariants. It is used by `binaryfuse.build` to encode fingerprints and by `binaryfuse.mayContain` to decode the three probe positions.

## Risks And Edge Cases
The code relies on exact output sizes, padding, little-endian interpretation, and unsafe pointer arithmetic. Unsupported bpv values panic. Odd value counts, partial groups, and zero-length input need to remain consistent with `EncodedSize`.

## Test Signals
Unit tests cover known encodings, round trips across random data and all widths, `Decode3`, and encode/decode benchmarks.
