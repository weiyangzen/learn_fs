# sources/storage-engines/foundationdb/cmake/CompileRocksDB.cmake

## Purpose
Configures FoundationDB's RocksDB dependency, generates an FDB RocksDB version header, finds a compatible system RocksDB when allowed, or builds RocksDB from a pinned release/commit.

## Important APIs, Types, and Functions
Uses `RocksDBVersion.cmake`, `FDBRocksDBVersion.h.in`, `find_package(RocksDB)`, `ExternalProject_Add(rocksdb)`, `ROCKSDB_LIBRARIES`, `ROCKSDB_INCLUDE_DIR`, and many RocksDB CMake args.

## Control Flow and Integration
The module validates that exactly one of `ROCKSDB_VERSION` or `ROCKSDB_GIT_HASH` is selected. For commit hashes it downloads `version.h` to parse major/minor/patch. It generates `FDBRocksDBVersion.h`, tries a system package only for version-based builds, then defines or imports the `rocksdb` build target.

## State and Persistence
Depends on network access for commit version probing/build downloads, SHA256 values, LZ4/liburing/sanitizer settings, and the custom `FindRocksDB.cmake`.

## Dependencies
Persists downloaded version checks, generated header under `fdbserver/core/include`, ExternalProject source/build directories, and target variables.

## Risks and Test Signals
Risks include configure-time network requirement, stale hash/version mismatch, system package overriding configured variables, and ABI mismatch from forwarded compiler flags. Test signals are generated header contents, RocksDB target byproducts, and fdbserver RocksDB storage tests.
