# sources/storage-engines/pebble/sstable/compressionanalyzer/block_analyzer.go

## Purpose
Analyzes individual SSTable/blob blocks by measuring compressibility and compression/decompression performance across predefined compression profiles.

## Important APIs, Types, and Functions
- `BlockAnalyzer` stores aggregate `Buckets`, compressors for every profile, decompressor instances, a MinLZFastest compressor for test compressibility, and scratch buffers.
- `NewBlockAnalyzer`, `ResetCompressors`, `Close`, `Block`, `Buckets`, `runExperiment`, and `ensureLen` manage lifecycle and measurement.

## Control Flow
`Block` classifies a block by size and MinLZFastest compressibility, updates uncompressed-size samples, and runs each profile experiment. `runExperiment` ensures scratch capacity, yields before timing, compresses, decompresses, verifies decompression through the decompressor API, and records weighted ns/byte and compression-ratio metrics.

## State and Persistence Behavior
No on-disk persistence. State accumulates in `Buckets` until `Close` or object discard. Adaptive compressors are reset per SSTable through `ResetCompressors` so cross-file history does not affect results.

## Dependencies and Integration Points
Used by `FileAnalyzer`. Depends on `internal/compression`, `block.Compressor`, `crtime`, `metricsutil` via `Buckets`, and block kinds.

## Risks and Edge Cases
Measurements are sensitive to scheduler noise despite `runtime.Gosched`. Scratch buffers grow to block size plus headroom. Panics on decompression errors rather than returning them. Compression profile state must be reset for fair per-file results.

## Test Signals
Indirectly exercised by `file_analyzer_test.go`, while bucket formatting and classification are covered by `buckets_test.go`.
