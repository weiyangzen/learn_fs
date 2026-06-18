# sources/storage-engines/foundationdb/fdbserver/worker/CMakeLists.txt

## Purpose
This CMake file defines the `fdbserver_worker` static library, its link smoke test, its unit-test target, include directories, and library dependencies.

## Important APIs, Types, And Functions
`fdb_find_sources(FDBSERVER_WORKER_SRCS)` discovers worker sources. `add_flow_target(STATIC_LIBRARY NAME fdbserver_worker ...)` creates the library. `add_fdbserver_link_test` builds a worker link-test target against the worker library and many fdbserver role libraries. `add_fdbserver_unit_test(fdbserver_worker_test worker ...)` defines the worker test executable. `configure_fdbserver_common_includes`, `target_include_directories`, and `target_link_libraries` configure compilation and linkage.

## Control Flow
CMake first discovers sources, creates the library, creates test/link targets, installs common include configuration, adds public and private include roots, and finally declares public/private link dependencies.

## State And Persistence Behavior
There is no runtime state or persistence. Build-system state is the set of source files, include paths, and dependency graph.

## Dependencies And Integration Points
The worker library publicly links `fdbctl` and privately links backup worker, cluster controller, commit proxy, consistency scan, coordinator, data distributor, GRV proxy, log router, log system, ratekeeper, resolver, sequencer, storage server, tester, tlog, and core libraries. The public include directory is `worker/include`; private includes include source and generated include trees.

## Risks And Test Signals
Because worker code references many roles, the link test helps catch missing symbols across role libraries. Dependency drift here can break actor-generated headers, role integrations, or worker unit-test linkage.
