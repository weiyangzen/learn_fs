# sources/storage-engines/pebble/internal/compression/compression_test.go

## Purpose
This file tests common compression factory behavior, round-trips for all presets, decompression error handling, and setting string parsing.

## Important APIs, Types, And Functions
`TestCompressionRoundtrip` iterates `presets`. `TestDecompressionError` builds malformed zstd-like bytes. Helper `decompress` uses `GetDecompressor`, `DecompressedLen`, and `DecompressInto`. `TestSettingString` checks `String` and `ParseSetting`.

## Control Flow
Round-trip tests create random payloads and random compressed output buffers, compress through a preset compressor, then decompress by returned algorithm and compare bytes. Error testing prefixes garbage with a plausible zstd decoded length and expects decompression failure. String testing loops all presets.

## State And Persistence Behavior
Tests are in-memory. No SST files are written. Leaktest wraps round-trip/error tests.

## Dependencies And Integration Points
It depends on `encoding/binary`, `math/rand/v2`, `leaktest`, `require`, and all compressor/decompressor implementations reachable from presets.

## Risks And Edge Cases
Tests cover payloads up to 10 KiB and malformed zstd, but not very large blocks except through `minlz_test.go`. The malformed zstd setup mutates only the varint prefix bytes, leaving payload as zeroed/garbage enough to expect an error.

## Test Signals
Signals are exact payload equality after decompression, non-nil error and nil result for bad zstd input, and successful preset string round-trips.
