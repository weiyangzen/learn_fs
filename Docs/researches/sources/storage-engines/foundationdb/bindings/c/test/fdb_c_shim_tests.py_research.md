# sources/storage-engines/foundationdb/bindings/c/test/fdb_c_shim_tests.py

## Purpose
Tests C shim and multi-version client behavior across current and previous FoundationDB binaries and client libraries.

## Important APIs, types, and functions
`TestEnv` extends `LocalCluster`, downloads versioned binaries, copies `libfdb_c` as an external client, and sets library paths. `FdbCShimTests` builds API tester args, runs C API workloads, unit tests, and shim library tester scenarios.

## Control flow
Runs default API workload and unit tests for the current version, then tests library discovery through `LD_LIBRARY_PATH`, explicit API path setting, environment variables, external/local library modes, invalid paths, lower API versions, and previous-release compatibility.

## State and persistence behavior
Creates temp clusters and copied client libraries, mutates workload data in those clusters, and cleans temp dirs after use.

## Dependencies and integration points
Depends on `FdbBinaryDownloader`, `LocalCluster`, shim/unit/api tester binaries, environment variables, previous release constants, and `CApiCorrectnessMultiThr.toml`.

## Risks and test signals
Expected abort return codes can be platform-sensitive; previous binary downloads can fail. Signals are exact process return codes and successful cross-version workload execution.
