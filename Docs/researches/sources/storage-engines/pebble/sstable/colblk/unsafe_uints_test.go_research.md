# sources/storage-engines/pebble/sstable/colblk/unsafe_uints_test.go

## Purpose
Validates and benchmarks zero-copy uint and offset accessors over serialized uint columns.

## Important APIs, Types, and Functions
- `TestUnsafeUints` generates values from each interesting integer range and row count, serializes with `UintBuilder`, decodes with `DecodeUnsafeUints`, and compares all values.
- For non-delta widths up to 4 bytes, it also decodes `UnsafeOffsets` and validates `At` and `At2`.
- `BenchmarkUnsafeUints` measures random `At` access across width/delta profiles.
- `BenchmarkUnsafeUintOffsets` measures offset-specialized access.
- `encodeRandUints`, `benchmarkUnsafeUints`, and `benchmarkUnsafeOffsets` are helpers.

## Control Flow
Tests build aligned buffers with an extra trailing padding byte, serialize values, decode, and compare every row. Benchmarks precompute random read indices to isolate accessor overhead.

## State and Persistence Behavior
The tests exercise serialized buffers created by the production `UintBuilder`, not hand-crafted bytes. The extra padding byte checks the same pointer-safety contract used in columnar block serialization.

## Dependencies and Integration Points
Depends on `interestingIntRanges`, `crbytes.AllocAligned`, randomized PCG generators, and the uint builder. It validates endian-specific `At` implementations indirectly.

## Risks and Edge Cases
Random seeds use wall-clock time, so failures require logged seed capture. Offset tests only apply where the encoding is legal for offsets.

## Test Signals
Strong round-trip coverage for every supported width class and delta mode, with performance baselines for hot unsafe access paths.
