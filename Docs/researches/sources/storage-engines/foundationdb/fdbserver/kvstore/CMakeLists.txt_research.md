# sources/storage-engines/foundationdb/fdbserver/kvstore/CMakeLists.txt

## Purpose
Defines the fdbserver KV-store static library, tests, include paths, and optional RocksDB/liburing linkage.

## Important APIs, Types, and Functions
- `fdb_find_sources(FDBSERVER_KVSTORE_SRCS)` discovers sources.
- `add_flow_target(STATIC_LIBRARY NAME fdbserver_kvstore ...)` builds the library.
- `add_fdbserver_link_test` and `add_fdbserver_unit_test(... kvstore ...)` register validation targets.
- `target_include_directories` exposes public/private include paths.
- `target_link_libraries` links `fdbserver_core`, sqlite, and optionally RocksDB/liburing/LZ4.
- `WITH_ROCKSDB` branch adds dependencies, includes, libraries, and `WITH_ROCKSDB` compile definition.

## Control Flow
CMake discovers sources, builds `fdbserver_kvstore`, configures tests/includes, links required dependencies, and conditionally extends the target for RocksDB support.

## State and Persistence Behavior
No runtime state; only build graph and feature-selection state.

## Dependencies and Integration Points
Integrates with `fdbserver_core`, sqlite, generated includes, RocksDB, liburing, and LZ4 depending on build options.

## Risks and Edge Cases
Automatic source discovery may include new files unexpectedly. Optional RocksDB/liburing branches change compile definitions and link interfaces.

## Test Signals
Registers `kvstore` unit-test and link-test targets.
