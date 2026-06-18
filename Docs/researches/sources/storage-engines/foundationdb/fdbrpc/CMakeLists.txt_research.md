# sources/storage-engines/foundationdb/fdbrpc/CMakeLists.txt

## Purpose
`CMakeLists.txt` defines how the fdbrpc static libraries, link test, fdbrpc test executable, optional coroutine/eio support, optional gRPC/protobuf bindings, benches, and subtests are built.

## Important APIs, Types, and Functions
Key CMake functions/macros include `fdb_find_sources`, `add_flow_target`, `target_link_libraries`, `target_include_directories`, `generate_grpc_protobuf`, `add_library`, `add_dependencies`, and `add_subdirectory`. Targets include `fdbrpc`, `fdbrpc_sampling`, `fdbrpclinktest`, `fdbrpc_test`, optional `eio`, and optional `coro`.

## Control Flow
The script gathers fdbrpc sources, removes standalone test/link sources from the library list, decides whether to compile bundled libeio, disables actor diagnostics for selected actor-heavy files, creates normal and sampling fdbrpc libraries, adds standalone tests, conditionally builds libeio/libcoroutine, configures include paths and libraries, conditionally generates gRPC protobuf code and links gRPC targets, enables sampling definitions, adds Windows actor dependency, and includes bench/tests subdirectories.

## State and Persistence Behavior
It does not affect runtime state. Its persistent effect is build graph structure, compile definitions, include directories, generated protobuf artifacts, and linked dependencies.

## Dependencies and Integration Points
It integrates fdbrpc with Flow, `libb64`, `md5`, `rapidjson`, optional `gRPC::grpc++`, protobuf include directories, generated proto targets, bundled `libeio`, bundled `libcoroutine`, Valgrind, bench builds, and fdbrpc tests.

## Risks and Edge Cases
Source auto-discovery can unexpectedly include new files unless explicitly removed. gRPC linking repeats `proto_fdbrpc_test` for `fdbrpc`, suggesting harmless duplication but possible maintenance drift. Cross-compiling skips benches. The coroutine path depends on `COROUTINE_IMPL` and platform-specific source choices. Third-party warning suppression hides diagnostics from bundled C code.

## Test Signals
Build success for `fdbrpc`, `fdbrpc_sampling`, `fdbrpclinktest`, and `fdbrpc_test` is the main signal. gRPC-enabled builds additionally validate protobuf generation and gRPC link dependencies.
