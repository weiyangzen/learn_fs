# sources/storage-engines/pebble/sstable/compressionanalyzer/buckets.go

## Purpose
Defines classification buckets and report formatting for compression analyzer results.

## Important APIs, Types, and Functions
- `BlockSize` categories: `Small`, `Medium`, `Large`, `Huge`.
- `MakeBlockSize` maps byte sizes to cutoff ranges.
- `Compressibility` categories: incompressible through highly compressible.
- `MakeCompressibility` maps uncompressed/compressed ratio to categories.
- `Profiles` lists Snappy, MinLZ1, Zstd1, adaptive Zstd profiles, and Zstd3.
- `Buckets`, `Bucket`, and `PerProfile` store Welford aggregates.
- `Buckets.String` and `Buckets.ToCSV` format tabular and CSV reports.
- `toMBPS` and `stdDevStr` convert timing and variability metrics.

## Control Flow
Formatting iterates all block kinds, size buckets, and compressibility buckets, skipping buckets below `minSamples`. For each included bucket, it prints average size, compression ratio, compression speed, and decompression speed for every profile.

## State and Persistence Behavior
All state is in-memory aggregate statistics. Reports are text/CSV snapshots derived from `metricsutil.Welford` and weighted Welford accumulators.

## Dependencies and Integration Points
Consumed by `BlockAnalyzer` and `FileAnalyzer` callers. Depends on `internal/compression`, `block.CompressionProfile`, `blockkind.All`, `metricsutil`, and tabwriter/time formatting.

## Risks and Edge Cases
Cutoff interpretation is encoded in both constants and `String`; changing cutoffs changes report compatibility. `MakeCompressibility` divides by compressed size and assumes nonzero compressed output. Formatting omits low-sample buckets, which can hide sparse data.

## Test Signals
Covered by `buckets_test.go` for block-size classification, compressibility classification, and deterministic example string/CSV output.
