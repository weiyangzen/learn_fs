# sources/storage-engines/rocksdb/tools/simulated_hybrid_file_system.cc

## Purpose
This file implements a development-only `FileSystemWrapper` that simulates hybrid storage by adding latency and IOPS throttling to warm files. It is designed for benchmark experiments that need slower warm-tier behavior while preserving warm-file membership across runs.

## Important APIs, Types, and Functions
`CalculateServeTimeUs()` models service time as fixed latency plus byte-dependent cost. `RateLimiterRequest()` adapts a byte-oriented `RateLimiter` to request-count-like timing. `SimulatedHybridFileSystem` loads/stores warm file metadata, wraps random-access and writable files, and removes deleted files from the warm set. `SimulatedHybridRaf` overrides `Read`, `MultiRead`, and `Prefetch`. `SimulatedWritableFile` overrides append, positioned append, and sync methods.

## Control Flow
Construction creates a generic rate limiter based on the throughput multiplier and loads newline-separated warm filenames from the metadata file when present. `NewRandomAccessFile` determines whether a file is warm based on full-FS mode or the warm set, creates the target file, then wraps it in `SimulatedHybridRaf`. `NewWritableFile` records warm files and wraps writes when appropriate. Reads and direct writes simulate wait immediately; buffered writes accumulate `unsynced_bytes` and simulate on `Sync`.

## State and Persistence
The warm-file set is protected by a mutex and persisted as a newline-separated metadata file in the destructor. `DeleteFile` removes entries from the set. Runtime state includes rate limiter tokens and unsynced byte counts.

## Dependencies and Integration Points
It depends on RocksDB `FileSystem`, `RateLimiter`, `StopWatchNano`, `Env::SleepForMicroseconds`, and file utility helpers. It integrates through `FileOptions::temperature` and RocksDB file creation/read paths.

## Risks
Constructor read failures call `std::exit(1)`, which is harsh for library code but intentional for benchmarks. `NewRandomAccessFile` wraps `result` even if target creation fails, which could be risky if callers expect `result` to be valid only on success. Warm metadata is unordered and rewritten only on destruction. The model is approximate and not production-safe.

## Test Signals
No direct tests are present in this subset. Benchmark runs using warm temperatures should show added latency/IOPS throttling and metadata persistence across process restarts.
