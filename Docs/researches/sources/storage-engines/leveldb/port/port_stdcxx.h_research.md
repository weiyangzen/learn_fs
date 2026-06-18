# sources/storage-engines/leveldb/port/port_stdcxx.h

## Purpose
`port_stdcxx.h` is the standard C++ portability layer behind `port/port.h`. It normalizes mutexes, condition variables, optional compression libraries, heap profiling hooks, and accelerated CRC32C access behind LevelDB-specific functions.

## Important APIs, Types, and Functions
The file defines `port::Mutex`, `port::CondVar`, `Snappy_Compress`, `Snappy_GetUncompressedLength`, `Snappy_Uncompress`, `Zstd_Compress`, `Zstd_GetUncompressedLength`, `Zstd_Uncompress`, `GetHeapProfile`, and `AcceleratedCRC32C`. Build-time feature flags `HAVE_SNAPPY`, `HAVE_ZSTD`, and `HAVE_CRC32C` decide whether these helpers call external libraries or return unsupported fallbacks.

## Control Flow
Configuration is discovered through `port/port_config.h` when present, then optional headers are included. Compression helpers allocate/resize destination strings, call the external codec, and return `false` on missing support or codec failure. `CondVar::Wait` temporarily adopts the already-held `Mutex` lock into `std::unique_lock`, waits, then releases ownership so the caller still owns the LevelDB lock.

## State, Dependencies, and Integration
State is limited to wrapped `std::mutex`/`std::condition_variable` members and temporary codec contexts. This layer is consumed by table format readers/writers, CRC verification, cache locking, env background queues, and tests. Risks include compile-time feature mismatch, zstd frame-size handling where unknown or zero size is treated as failure, and `AcceleratedCRC32C` returning zero when unavailable.

## Test Signals
Coverage is indirect through table compression tests, CRC tests, cache/env synchronization tests, and builds with and without optional libraries.
