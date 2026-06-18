## sources/storage-engines/foundationdb/bindings/flow/CMakeLists.txt

Purpose: build definition for the `fdb_flow` static library and its tester/package targets.

Important targets: `SRCS` lists directory layer, partition/subspace, loaner types, high contention allocator, tuple, and Flow C API wrapper sources. `add_flow_target(STATIC_LIBRARY NAME fdb_flow ...)` builds the library. It links `fdb_c` and `fdbclient`, exposes include directories, and adds the `tester` subdirectory.

Control flow: for non-IDE builds it collects headers, computes snapshot suffix, creates package directories, defines a tarball custom command copying the library and headers, adds `package_flow`, and hooks it into `packages`.

State and persistence: build artifacts include a static library and optional `fdb-flow-<version>` tarball under build package directories.

Dependencies and integration points: integrates Flow bindings with the top-level CMake helpers, FDB version variables, package aggregation, `fdb_c`, `fdbclient`, and tester executable.

Risks: packaging assumes x86_64 tarball naming and copies only headers detected from `SRCS`. Missing a header in `SRCS` can omit it from package output.

Test signals: successful build of `fdb_flow` and `fdb_flow_tester` validates compile/link integration.
