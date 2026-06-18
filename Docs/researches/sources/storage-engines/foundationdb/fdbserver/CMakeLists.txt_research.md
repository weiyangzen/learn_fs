# sources/storage-engines/foundationdb/fdbserver/CMakeLists.txt

## Purpose
This CMake file defines how the main `fdbserver` executable and its component libraries are assembled. It discovers fdbserver sources, excludes workload sources from the main source list, adds many server subdirectories, configures optional RocksDB/liburing/Swift/Jemalloc/gperftools support, links server component libraries, and installs the server binary.

## Important APIs, Types, And Functions
Important build helpers include `fdb_find_sources`, `configure_fdbserver_common_includes`, `configure_fdbserver_target_includes`, `add_flow_target`, `add_subdirectory`, `add_swift_to_cxx_header_gen_target`, `generate_modulemap`, `fdb_install`, and optional package helpers such as `find_package(LZ4)`, `find_package(uring)`, `include(CompileRocksDB)`, `include(FindSwiftLibs)`, `include(SwiftToCXXInterop)`, and `include(GenerateModulemap)`.

## Control Flow
The script first gathers `FDBSERVER_SRCS`, removes workload files and `FDBServerUnitTestMain.cpp`, and defines include helper functions. It configures RocksDB dependencies if enabled, adds server subsystem subdirectories, creates a workload binary directory, and defines the `fdbserver` executable. Under `WITH_SWIFT`, it defines `fdbserver_swift`, configures Swift/C++ include paths and compile flags, generates Swift-to-C++ headers, wires dependencies among Flow, fdbrpc, fdbclient, and fdbserver actor targets, links Swift object files into `fdbserver`, and generates a module map. It then configures includes and links the server against all component libraries, RocksDB or normal storage dependencies, memory/profiling libraries, TOML/RapidJSON, optional Swift libraries, install rules, and public `fdbctl`.

## State And Persistence Behavior
The file controls generated build state: source lists, target dependency graph, generated Swift headers/module maps, object-file link options, compile definitions, install outputs, and generated package binaries. It does not define runtime persistence, but build options such as RocksDB/liburing directly change the storage engine code linked into the server.

## Dependencies And Integration Points
It is the integration hub for fdbserver submodules: `core`, `kvstore`, `logsystem`, `mocks3`, `clustercontroller`, `backupworker`, `commitproxy`, `coordinator`, `datadistributor`, `consistencyscan`, `grvproxy`, `logrouter`, `ratekeeper`, `resolver`, `sequencer`, `storageserver`, `tester`, `tlog`, `worker`, and `workloads`. It links external dependencies including `fdbclient`, `sqlite`, RocksDB, LZ4, liburing, Jemalloc, TOML11, RapidJSON, Swift runtime libraries, gperftools, and `fdbctl`.

## Risks And Test Signals
Swift integration is fragile because it relies on generated headers, virtual filesystem overlays, object-library link options, and explicit target dependencies. RocksDB with liburing changes compile definitions to disable epoll and enable io_uring in Boost.Asio. `WHOLE_ARCHIVE` on workloads intentionally preserves workload registrations but can increase link sensitivity. Primary signals are successful configure/generate for combinations of `WITH_SWIFT`, `WITH_ROCKSDB`, `WITH_LIBURING`, `USE_JEMALLOC`, and `GPERFTOOLS_FOUND`, plus successful `fdbserver` link, generated Swift headers/module map, and packaging install paths.
