# sources/storage-engines/pebble/internal/compression/minlz.go

## Purpose
This file implements MinLZ compression/decompression adapters for the package compression interfaces.

## Important APIs, Types, And Functions
`minlzCompressor` stores a level and implements `Compress` and `Close`; `getMinlzCompressor` returns singleton fastest or balanced compressors. `minlzDecompressor` implements `DecompressInto`, `DecompressedLen`, and `Close`.

## Control Flow
Compression falls back to Snappy if the source exceeds `minlz.MaxBlockSize`; otherwise it calls `minlz.Encode`, panics on unexpected encode error, marks bytes for MSan, and returns a MinLZ setting. Decompression calls `minlz.Decode` into the supplied buffer, verifies the returned slice aliases the buffer exactly, marks bytes for MSan, and returns errors for decode or alias/length mismatch.

## State And Persistence Behavior
The singleton compressors are stateless except for level. Compressed blocks are persisted by callers, and the returned setting may be Snappy for oversized MinLZ inputs.

## Dependencies And Integration Points
It depends on `github.com/minio/minlz`, `snappyCompressor` fallback, `base.CorruptionErrorf`, and `msanWrite`.

## Risks And Edge Cases
The important edge case is oversized blocks. `minlz_test.go` also asserts MinLZ decompressor can decode Snappy fallback bytes, implying MinLZ decode compatibility or wrapper behavior must remain true. Buffer alias checks catch decompression APIs allocating or writing somewhere unexpected.

## Test Signals
`minlz_test.go` validates boundary sizes around `MaxBlockSize`, fallback behavior, and decompression equality.
