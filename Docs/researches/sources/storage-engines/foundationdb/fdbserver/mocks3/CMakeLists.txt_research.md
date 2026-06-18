# sources/storage-engines/foundationdb/fdbserver/mocks3/CMakeLists.txt

## Purpose
Builds the FoundationDB mock S3 server support library and its unit test target.

## Important APIs, Types, And Functions
Uses `fdb_find_sources(FDBSERVER_MOCKS3_SRCS)`, `add_flow_target(STATIC_LIBRARY NAME fdbserver_mocks3 ...)`, `add_fdbserver_unit_test(fdbserver_mocks3_test mocks3 ...)`, `configure_fdbserver_common_includes()`, include-directory configuration, and `target_link_libraries()`.

## Control Flow
CMake discovers mock S3 sources, builds them into the static `fdbserver_mocks3` library, registers `fdbserver_mocks3_test` with dependencies on `fdbserver_mocks3`, `fdbserver_core`, and `fdbclient`, exposes the local `include` directory publicly, adds RapidJSON privately, and links `fdbclient`.

## State And Persistence Behavior
No runtime state is managed. Build state consists of generated targets, include paths, and link dependencies in the CMake graph.

## Dependencies And Integration Points
Integrates the mock S3 library into FoundationDB's Flow/FDB server build system and unit-test infrastructure. RapidJSON is required privately by `MockS3Server.cpp` persistence metadata serialization.

## Risks And Edge Cases
If source discovery omits a new mock S3 source or RapidJSON include path changes, the target or tests fail to compile. Public include exposure is required for consumers of `fdbserver/mocks3/*.h`.

## Test Signals
Successful configuration/build of `fdbserver_mocks3` and execution/registration of `fdbserver_mocks3_test` are the primary signals.
