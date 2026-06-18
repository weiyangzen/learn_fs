# sources/storage-engines/pebble/sstable/runlength_bitmap.go

## Purpose
Implements a compact run-length encoding for bitmaps that are written in increasing set-bit order and read sequentially. It is optimized for spatial locality, especially long all-zero or all-one byte runs.

## Important APIs, Types, And Functions
`BitmapRunLengthEncoder` exposes `Init`, `Set`, `FinishAndAppend`, and `Size`. `IterSetBitsInRunLengthBitmap` returns an `iter.Seq[int]` yielding set bit indexes from an encoded bitmap.

## Control Flow And State
The encoder buffers one current byte (`currByte`) and its byte index, plus a pending run length for consecutive all-set bytes. `Set(i)` requires monotonically increasing indexes, folds bits into the current byte when possible, flushes mixed bytes directly, encodes all-zero gaps as `0x00` followed by a uvarint byte count, and encodes all-one runs as `0xFF` followed by a uvarint byte count. Mixed bytes are stored literally, excluding `0x00` and `0xFF` because those byte values signal runs.

The decoder scans encoded bytes, treating `0x00` as a zero-run skip, `0xFF` as a set-run yield loop, and all other bytes as literal bit masks. `Size` estimates the final encoded length without mutating the pending state.

## Persistence And Integration
The encoded byte slice is intended to be embedded in SSTable metadata or related table structures that need compact sequential bitmap scans. The file itself is independent of disk I/O and returns bytes through caller-provided buffers.

## Dependencies
Uses `encoding/binary` for uvarints, Go's `iter` package for sequence iteration, and `invariants.MaybeMangle` to catch stale buffer assumptions during reset.

## Risks
`Set` assumes strictly increasing indexes; out-of-order calls are not checked and would corrupt logical output. `IterSetBitsInRunLengthBitmap` assumes valid encodings; it does not handle malformed/truncated uvarints. All-one runs can yield many indexes, so decoding intentionally scales with the number of set bits.

## Test Signals
`runlength_bitmap_test.go` provides datadriven exact encoding checks plus randomized round-trip coverage that decodes and re-encodes generated bitmaps.
