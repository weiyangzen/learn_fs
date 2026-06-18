# sources/storage-engines/foundationdb/cmake/FindRocksDB.cmake

## Purpose
Finds a system RocksDB installation and extracts its version.

## Important APIs, Types, and Functions
Searches `ROCKSDB_INCLUDE_DIR`, parses `rocksdb/version.h` macros, finds `ROCKSDB_LIBRARY`, and sets `ROCKSDB_FOUND`, `ROCKSDB_VERSION`, include/library variables.

## Control Flow and Integration
`CompileRocksDB.cmake` calls this only for configured release-version builds. If it fails, `CompileRocksDB.cmake` restores configured version and builds RocksDB externally.

## State and Persistence
Depends on `ROCKSDB_ROOT`/environment root and RocksDB's standard include layout.

## Dependencies
No generated state; result variables are cached/advanced.

## Risks and Test Signals
Risks include overwriting `ROCKSDB_VERSION` used for configured version selection and accepting ABI-incompatible system libraries. Test signal is version message and successful fdbserver link.
