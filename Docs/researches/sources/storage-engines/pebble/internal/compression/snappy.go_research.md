# sources/storage-engines/pebble/internal/compression/snappy.go

## Purpose
This file adapts Go Snappy compression/decompression to Pebble's compression interfaces.

## Important APIs, Types, And Functions
`snappyCompressor` implements `Algorithm`, `Compress`, and `Close`. `snappyDecompressor` implements `DecompressInto`, `DecompressedLen`, and `Close`.

## Control Flow
Compression calls `snappy.Encode` with capacity-limited destination, marks the result for MSan, and returns `SnappySetting`. Decompression calls `snappy.Decode` into the provided buffer, verifies length and aliasing, marks the destination for MSan, and returns errors on decode or buffer mismatch. `DecompressedLen` delegates to `snappy.DecodedLen`.

## State And Persistence Behavior
The codec is stateless. Snappy-compressed bytes are persisted by callers in SST blocks.

## Dependencies And Integration Points
It depends on `github.com/golang/snappy`, `base.CorruptionErrorf`, and `msanWrite`. It is used directly by factories and as MinLZ fallback for oversized inputs.

## Risks And Edge Cases
The aliasing check is important because callers expect decompression into a manually/accounted buffer. Compression uses `dst[:cap(dst):cap(dst)]`, which lets Snappy reuse full capacity.

## Test Signals
Common compression round-trip tests exercise Snappy. MinLZ large-block tests may exercise Snappy fallback paths.
