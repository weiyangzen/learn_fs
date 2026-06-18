# sources/storage-engines/pebble/internal/compression/noop.go

## Purpose
This file implements the no-compression codec for the package interfaces.

## Important APIs, Types, And Functions
`noopCompressor` implements `Compress` and `Close`. `noopDecompressor` implements `DecompressInto`, `DecompressedLen`, and `Close`.

## Control Flow
Compression copies `src` into `dst[:0]` and returns `NoCompression`. Decompression copies `src` into `dst` after slicing to source length. Decompressed length is simply `len(b)`.

## State And Persistence Behavior
The codec is stateless. It represents uncompressed persisted blocks; callers still treat it through the same compressor/decompressor abstraction.

## Dependencies And Integration Points
It is returned by `GetCompressor(NoAlgorithm)` and `GetDecompressor(NoAlgorithm)` and is used by adaptive compression tests as a fast codec.

## Risks And Edge Cases
Callers must allocate a destination of the exact decompressed length before `DecompressInto`; this implementation assumes `dst` is large enough. It does not validate aliasing or return corruption errors.

## Test Signals
`compression_test.go` round-trips the `NoCompression` preset through the common factory path.
