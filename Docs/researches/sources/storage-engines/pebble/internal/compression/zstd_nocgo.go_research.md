# sources/storage-engines/pebble/internal/compression/zstd_nocgo.go

## Purpose
This file implements Zstd compression/decompression using the pure-Go klauspost library when cgo is unavailable or `pebblegozstd` is set.

## Important APIs, Types, And Functions
`zstdCompressor` holds a level and `*zstd.Encoder`, with a pool for wrapper structs. `UseStandardZstdLib` is false. `Compress`, `Close`, and `getZstdCompressor` implement compression. Stateless `zstdDecompressor` implements `DecompressInto`, `DecompressedLen`, `Close`, and `getZstdDecompressor`.

## Control Flow
Compression writes a varint decoded-length prefix into `compressedBuf`, encodes all bytes with the configured encoder appending after the prefix, marks the result, and returns Zstd setting. `Close` closes the encoder, clears it, and returns the wrapper to a pool. Decompression reads the prefix, creates a new decoder, decodes into `dst[:0]`, verifies length and aliasing, marks bytes, and closes the decoder.

## State And Persistence Behavior
Persisted block format matches the cgo variant's varint length prefix. Encoder state is per compressor and must be closed; decompressor creates a decoder per call.

## Dependencies And Integration Points
It depends on `github.com/klauspost/compress/zstd`, `encoding/binary`, `base`, and `msanWrite`. It is selected by build tags through `compression.go` factories.

## Risks And Edge Cases
Pure-Go zstd may produce different compressed bytes from the standard library, so reproducibility-sensitive tests check `UseStandardZstdLib`. Per-call decoder allocation can be more expensive than pooled cgo contexts.

## Test Signals
Compression round-trips and decompression-error tests exercise this path in non-cgo or `pebblegozstd` builds.
