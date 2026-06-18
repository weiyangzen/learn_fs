# sources/sync-backup/kopia/repo/compression/compressor_test.go

Purpose: validates all supported compressors for round-trip correctness, header isolation, rough compression behavior, and benchmark performance.

Important APIs/types/functions: `TestCompressor` iterates `ByHeaderID`, skipping unsupported IDs; `BenchmarkCompressor`, `compressionBenchmark`, and `decompressionBenchmark` iterate supported names from `ByName`.

Control flow: for each supported compressor, the test compresses zero data and expects output smaller than input, verifies every other compressor rejects the header, decompresses with the correct compressor, then repeats with random data expecting it not to shrink. Benchmarks cover zero, repeated-pattern, and random data for compression/decompression.

State and persistence behavior: all data is in memory buffers. The test exercises the persisted four-byte header contract by passing full compressed data to `Decompress(..., withHeader=true)`.

Dependencies/integration: depends on crypto random data, sorted compressor names, testutil `TestMain`, and the global compression registry.

Risks and edge cases: the random-data non-compression assertion is heuristic but reasonable for the registered algorithms. Unsupported compressors are skipped, so LZ4 unsupported behavior is not directly asserted.

Test signals: failures indicate broken compressor registration, header collisions, wrong-header acceptance, round-trip corruption, or unexpectedly poor/basic compression behavior.
