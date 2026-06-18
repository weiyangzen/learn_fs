# sources/storage-engines/pebble/internal/compression/zstd_cgo.go

## Purpose
This file implements Zstd compression/decompression using the DataDog CGo-backed zstd library when cgo is enabled and `pebblegozstd` is not set.

## Important APIs, Types, And Functions
`zstdCompressor` holds a level and `zstd.Ctx`; compressor instances are pooled. `UseStandardZstdLib` is true for test reproducibility. `Compress`, `Close`, and `getZstdCompressor` implement compression. `zstdDecompressor` with a pooled context implements `DecompressInto`, `DecompressedLen`, `Close`, and `getZstdDecompressor`.

## Control Flow
Compression reserves a varint prefix for decoded length, ensures capacity using `zstd.CompressBound`, writes the length, compresses into the buffer after the prefix, asserts no unexpected allocation, marks compressed bytes, and returns a Zstd setting. Decompression reads the varint length prefix, rejects empty source/destination, decompresses into `dst`, validates byte count, marks bytes, and reports corrupted length prefixes.

## State And Persistence Behavior
Compressed blocks include a uvarint decoded-length prefix. Compressor/decompressor contexts are pooled and must be closed to return them.

## Dependencies And Integration Points
It depends on `github.com/DataDog/zstd`, `encoding/binary`, `base`, and `msanWrite`. It is selected by build tags and returned by the common factories.

## Risks And Edge Cases
Risks include context reuse without `Close`, invalid varint prefixes, zero-length buffers, compression library allocation changes, and cgo availability. Tests may branch on `UseStandardZstdLib`.

## Test Signals
Common compression round-trip and malformed zstd tests exercise this implementation in cgo builds.
