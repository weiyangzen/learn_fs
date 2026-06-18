# sources/storage-engines/foundationdb/fdbclient/CMakeLists.txt

## Purpose

This CMake file defines the build graph for the `fdbclient` static library, generated option bindings, the sampling-enabled client variant, the `s3client` executable, optional Swift support, optional Azure/AWS backup integrations, link tests, and client-focused tests.

## Important Targets And Build APIs

`fdb_find_sources(FDBCLIENT_SRCS)` discovers client sources, then removes standalone/test entry points and appends `sha1/SHA1.cpp`. The build requires `VEXILLOGRAPHER_COMMAND`; it generates `include/fdbclient/FDBOptions.g.h` and `.cpp` from `fdbclient/vexillographer/fdb.options`, and separately generates the C option header via `vexillographer_compile()`. `fdboptions` is an `ALL` custom target depended on by downstream targets.

`add_flow_target(STATIC_LIBRARY NAME fdbclient ...)` builds the main client library with generated option sources. It publishes source and generated include directories and links `fdbrpc` and `msgpack` publicly while keeping `rapidxml` private. `fdbclient_sampling` repeats the library build with `fdbrpc_sampling` and `ENABLE_SAMPLING`, allowing server-side code to retain sampling without imposing it on pure clients.

`s3client` is built as a Flow executable with explicit include directories for Flow, fdbrpc, md5, libb64, Boost, and generated headers, and links the client, Flow/RPC libraries, compression/hash/support libraries, Boost program options, and platform coroutine/memcpy libraries as needed.

## Control Flow

Configuration first generates headers and build flags, then conditionally augments sources and definitions for Azure and AWS backup. Azure support bootstraps an external `azure-storage-lite` build through configure/build `execute_process()` calls before adding the generated subdirectory. Swift support creates `fdbclient_swift`, generates a module map, wires Swift compiler overlays, and links Swift object files into `fdbclient`.

## State And Persistence

The persistent outputs are generated headers/sources in `${CMAKE_CURRENT_BINARY_DIR}/include/fdbclient/`, configured `BuildFlags.h` and `versions.h`, optional downloaded Azure source/build trees, and CMake targets. The file caches `FDB_OPTIONS_H` for use by other build logic.

## Dependencies And Integration Points

The file depends on repository CMake functions/macros such as `add_flow_target`, `fdb_find_sources`, `vexillographer_compile`, and optional modules `awssdk`, `FindSwiftLibs`, and `GenerateModulemap`. It is the integration point between `fdbclient` actor compilation, generated public option APIs, backup storage providers, Swift interop, and test registration.

## Risks And Test Signals

Hard-coded Boost include path usage in `s3client` can be brittle outside the expected build image. Azure bootstrapping performs configure/build during CMake configuration, so failures surface early and can make reproducibility sensitive to generator and network/cache state. The tests registered on non-Windows non-IDE builds are `s3client_test`, `gcs_client_test` with `USE_MOCK_GCS=true`, and `bulkload_test`; link correctness is also checked by `fdbclientlinktest` and the excluded-by-default `fdbclient_test`.
