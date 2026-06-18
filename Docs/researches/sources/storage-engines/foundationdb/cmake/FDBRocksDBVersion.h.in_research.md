# sources/storage-engines/foundationdb/cmake/FDBRocksDBVersion.h.in

## Purpose
Template for the generated C++ header that exposes the RocksDB version compiled into FoundationDB.

## Important APIs, Types, and Functions
Defines include guard and macros `FDB_ROCKSDB_MAJOR`, `FDB_ROCKSDB_MINOR`, `FDB_ROCKSDB_PATCH`, and `FDB_ROCKSDB_GIT_HASH`.

## Control Flow and Integration
`CompileRocksDB.cmake` configures this file into `fdbserver/core/include/fdbserver/core/FDBRocksDBVersion.h` during CMake configure.

## State and Persistence
Depends on version variables parsed from `RocksDBVersion.cmake` or downloaded RocksDB `version.h`.

## Dependencies
Generated header persists in the build include tree and should not be committed.

## Risks and Test Signals
Risks are stale generated headers after changing RocksDB config and empty git hash semantics for release builds. Test signals are compile-time use from RocksDB storage code and generated macro values.
