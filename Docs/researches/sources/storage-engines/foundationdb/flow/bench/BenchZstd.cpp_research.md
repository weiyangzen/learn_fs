# sources/storage-engines/foundationdb/flow/bench/BenchZstd.cpp

Purpose: benchmarks raw and streaming Zstandard compression/decompression when `ZSTD_LIB_SUPPORTED` is enabled.

Important APIs/types/functions: helpers `compress`, `compress2`, `decompress`, `compressAsStream`, `decompressAsStream`, `genUncompressedData`, `genCompressedData`; benchmark functions for compress, compress2, stream compress, decompress, and stream decompress.

Control flow: test data comes from `BM_ZSTD_DATA` if set or a deterministic 1 MiB alphanumeric string. Static globals hold uncompressed data and compressed data at levels 1, 3, and 9. Benchmarks iterate through chunks using selected chunk size/level, track compression ratio counters, and set bytes processed.

State/persistence: process-static `UNCOMPRESSED` and `COMPRESSED` cache benchmark inputs. Compression contexts/streams are created per benchmark function invocation and freed where implemented.

Dependencies/integration: Google Benchmark, Flow deterministic random, and zstd C API under conditional compilation.

Risks: several helper calls do not check `ZSTD_isError`, so failed compression/decompression can be misinterpreted. `compress2` creates a `ZSTD_CCtx` without visible free, and stream reuse semantics may carry state if not reset per chunk as expected by the API.

Test signals: registered argument matrix covers chunk sizes from 4 KiB to 8 MiB and levels 1/3/9, plus decompression by level.
