# sources/storage-engines/foundationdb/fdbserver/core/CMakeLists.txt

## Purpose
Defines the `fdbserver_core` static library target, its coroutine implementation source, tests, include paths, and optional RocksDB dependencies.

## Important APIs, Types, and Functions
- `fdb_find_sources(FDBSERVER_CORE_LOCAL_SRCS)` discovers local sources.
- `add_flow_target(STATIC_LIBRARY NAME fdbserver_core ...)` builds the core library.
- `add_fdbserver_link_test()` and `add_fdbserver_unit_test()` add link and unit-test coverage.
- `configure_fdbserver_common_includes()` and `target_include_directories()` configure public/private include paths.
- The `WITH_ROCKSDB` block adds RocksDB, optional liburing, LZ4, and compile definitions.

## Control Flow
CMake collects local sources, appends either `CoroFlowCoro.actor.cpp` or `CoroFlow.actor.cpp` based on `COROUTINE_IMPL`, creates the target, attaches tests, configures includes, links `fdbclient`, and conditionally wires RocksDB support.

## State and Persistence Behavior
No runtime state. Build state is expressed as target dependencies, include directories, link libraries, and compile definitions.

## Dependencies and Integration Points
Integrates with the repository's Flow/CMake helper functions, fdbserver include generation, fdbclient, RocksDB, liburing, and LZ4. It is the build aggregation point for the core files in this subset.

## Risks and Edge Cases
Source discovery makes target composition sensitive to generated or misplaced files in this directory. RocksDB include/link behavior differs depending on `WITH_LIBURING`; missing libraries or incorrect definitions would affect bulk load/dump SST utilities.

## Test Signals
The build file declares `fdbserver_corelinktest` and `fdbserver_core_test`, which are primary signals that core sources link and embedded unit tests compile/run.
