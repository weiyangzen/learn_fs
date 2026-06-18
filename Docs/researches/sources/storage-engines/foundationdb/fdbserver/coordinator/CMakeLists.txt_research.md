# sources/storage-engines/foundationdb/fdbserver/coordinator/CMakeLists.txt

## Purpose
This build file defines the coordinator module as a static Flow actor library and wires its link tests, unit tests, include directories, and dependencies. The module contains coordinator server logic and on-demand durable store support, based on the file list in the same directory.

## Important build APIs
`fdb_find_sources(FDBSERVER_COORDINATOR_SRCS)` gathers coordinator sources. `add_flow_target(STATIC_LIBRARY NAME fdbserver_coordinator SRCS ...)` builds them as a Flow-aware static library. `add_fdbserver_link_test(fdbserver_coordinatorlinktest fdbserver_coordinator fdbserver_kvstore fdbserver_core)` validates linkage with core and kvstore dependencies. `add_fdbserver_unit_test(fdbserver_coordinator_test coordinator ...)` registers coordinator unit tests. `configure_fdbserver_common_includes` applies shared include paths. Public includes are exported from `include`, while private includes include the source and binary directories. The library privately links `fdbserver_core` and `fdbserver_kvstore`.

## Control flow, state, and persistence
This file has no runtime control flow. Its dependency choices indicate that coordinator code integrates with core server interfaces and key-value store persistence. The private binary include directory suggests generated/configured headers may be consumed internally. Runtime persistence details are in `Coordination.cpp`, `OnDemandStore.cpp`, and related headers rather than this CMake file.

## Dependencies and integration points
The coordinator library is built as a reusable fdbserver component with public headers under `fdbserver/coordinator`. It depends on `fdbserver_kvstore` for durable local storage and `fdbserver_core` for shared actor/server infrastructure. The unit test target names the suite category `coordinator`, making this module explicitly testable outside full simulation.

## Risks and test signals
The build file is small but important: missing dependencies would surface as link-test failures, and missing public include paths would break downstream role wiring. The explicit unit test target is a strong signal that coordinator logic has dedicated tests. Because this CMake target exports only the `include` directory publicly, internal headers such as `OnDemandStore.h` remain private unless included through the private source path by module sources.
