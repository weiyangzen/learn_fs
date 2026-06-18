# sources/storage-engines/pebble/internal/compression/compression.go

## Purpose
This file defines Pebble's internal compression abstraction: algorithm identifiers, compression settings, presets, compressor/decompressor interfaces, and factory functions.

## Important APIs, Types, And Functions
`Algorithm` includes `NoAlgorithm`, `Snappy`, `MinLZ`, `Zstd`, `NumAlgorithms`, and `Unknown`. `Setting` stores algorithm plus optional level and supports `String`/`ParseSetting`. Presets include `NoCompression`, `SnappySetting`, MinLZ levels, and Zstd levels. `Compressor` and `Decompressor` define `Compress`, `DecompressInto`, `DecompressedLen`, and `Close`. `GetCompressor`, `GetDecompressor`, and `makePreset` dispatch implementations.

## Control Flow
Factories switch on the algorithm and return no-op, Snappy, MinLZ, or build-selected Zstd implementations. `ParseSetting` scans known algorithms by string prefix and parses a numeric suffix as level.

## State And Persistence Behavior
The `presets` slice is package-global and populated as preset vars initialize. Compression settings are stored in table/block metadata elsewhere; this file does not persist state itself.

## Dependencies And Integration Points
It imports MinLZ level constants and dispatches to `noop.go`, `snappy.go`, `minlz.go`, and `zstd_*`. SSTable/block code depends on these interfaces for codec-independent compression.

## Risks And Edge Cases
Invalid algorithms panic in factories. `ParseSetting` accepts any numeric suffix that fits in `uint8` after conversion, so callers must validate if needed. String names are part of diagnostics and test expectations.

## Test Signals
`compression_test.go` round-trips every preset, checks zstd decompression errors, and validates `Setting.String`/`ParseSetting` round-trip.
