# sources/storage-engines/foundationdb/fdbserver/consistencyscan/CMakeLists.txt

## Purpose
This build file defines the consistency scan module as a static Flow actor library and wires its public include directory, common fdbserver includes, core dependency, and link test.

## Important build APIs
`fdb_find_sources(FDBSERVER_CONSISTENCYSCAN_SRCS)` gathers module sources. `add_flow_target(STATIC_LIBRARY NAME fdbserver_consistencyscan SRCS ...)` builds them as a Flow-aware static library. `add_fdbserver_link_test(fdbserver_consistencyscanlinktest fdbserver_consistencyscan fdbserver_core)` creates a link-time sanity target. `configure_fdbserver_common_includes(fdbserver_consistencyscan)` applies shared include configuration. `target_include_directories(... PUBLIC include)` exports the module's public headers. `target_link_libraries(... PRIVATE fdbserver_core)` links the implementation to core server functionality.

## Control flow and integration
The file has no runtime control flow. It integrates `ConsistencyScan.cpp` and its header into the fdbserver build graph. The public include directory exposes `fdbserver/consistencyscan/ConsistencyScan.h` to modules and workloads that call `consistencyScan`, `getKeyServers`, `getKeyLocations`, or `checkDataConsistency`.

## State and persistence behavior
Build configuration only; no persistent runtime state. The important persistence implication is indirect: linking this module brings in code that reads and writes `ConsistencyScanState` keys in the system database and issues low-priority storage server reads.

## Dependencies, risks, and test signals
The library links privately to `fdbserver_core`, which supplies worker interfaces, knobs, storage metrics, ratekeeper/server DB info, simulation policy, and system metadata utilities. The link test catches unresolved symbols caused by missing source files or dependencies. A risk observed while reading the sources is that the public header declares `getVersion(Database cx)`, but the implementation defines `getStorageServerReadVersion(Database cx)` instead; this CMake link test may not catch that mismatch unless a consumer references `getVersion`.
