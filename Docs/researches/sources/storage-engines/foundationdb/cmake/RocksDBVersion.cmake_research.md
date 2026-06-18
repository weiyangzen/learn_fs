# sources/storage-engines/foundationdb/cmake/RocksDBVersion.cmake

## Purpose
Source-controlled configuration selecting the RocksDB release or commit used by FoundationDB.

## Important APIs, Types, and Functions
Currently sets `ROCKSDB_VERSION` to `9.7.3` and `ROCKSDB_VERSION_SHA256`; alternative commented variables allow `ROCKSDB_GIT_HASH` and `ROCKSDB_GIT_HASH_SHA256`.

## Control Flow and Integration
`CompileRocksDB.cmake` includes this file, validates mutual exclusivity, generates version macros, and builds/downloads RocksDB using these values.

## State and Persistence
Depends on RocksDB GitHub archive naming and maintainers keeping SHA256 values synchronized.

## Dependencies
State is source-controlled CMake variables; no generated files here.

## Risks and Test Signals
Risks include enabling both options, wrong SHA256, or changing version without updating generated-header expectations. Test signal is successful `CompileRocksDB.cmake` configure and archive verification.
