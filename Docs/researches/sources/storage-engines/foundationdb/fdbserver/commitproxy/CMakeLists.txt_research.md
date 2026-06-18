# sources/storage-engines/foundationdb/fdbserver/commitproxy/CMakeLists.txt

## Purpose
`CMakeLists.txt` defines the `fdbserver_commitproxy` static library target for the commit proxy server component. It discovers source files in the directory, configures common server includes, exposes the component's public include directory, adds private source/binary include paths, links required server libraries, and creates a link test target.

## Important APIs, Types, and Functions
- `fdb_find_sources(FDBSERVER_COMMITPROXY_SRCS)` populates the component source list from the current directory according to FoundationDB's CMake conventions.
- `add_flow_target(STATIC_LIBRARY NAME fdbserver_commitproxy SRCS ${FDBSERVER_COMMITPROXY_SRCS})` creates the Flow-enabled static library.
- `add_fdbserver_link_test(fdbserver_commitproxylinktest fdbserver_commitproxy fdbserver_logsystem fdbserver_core)` adds a link-only validation target for dependency completeness.
- `configure_fdbserver_common_includes(fdbserver_commitproxy)` applies common include configuration.
- `target_include_directories` publishes `${CMAKE_CURRENT_SOURCE_DIR}/include` and privately includes the source and binary dirs.
- `target_link_libraries(fdbserver_commitproxy PRIVATE fdbserver_core fdbserver_kvstore fdbserver_logsystem)` sets private link dependencies.

## Control Flow
CMake evaluates the file during configure/generate. Source discovery runs first, then the library target is created, the link-test target is declared, include paths are attached, and private dependencies are linked. There is no runtime control flow.

## State and Persistence Behavior
The file persists build graph state only: target names, include visibility, discovered source membership, and static-library dependencies. Generated build files encode this state, but no database or runtime state is touched.

## Dependencies and Integration Points
This component integrates with FoundationDB's custom CMake helpers for Flow actor compilation and server target setup. It depends on `fdbserver_core`, `fdbserver_kvstore`, and `fdbserver_logsystem`, which indicates commit proxy code uses core server interfaces, key-value store support, and log-system types. The public include directory allows downstream targets to include commitproxy headers.

## Risks and Edge Cases
Automatic source discovery can accidentally include or omit files if naming/location conventions are not followed. A missing dependency may pass compilation through transitive includes but fail the explicit link test, so the link test is important. Public include exposure should remain limited to headers intended for other components; moving private headers under `include` broadens the component API. Generated files that require `${CMAKE_CURRENT_BINARY_DIR}` must be produced before compilation by other build rules.

## Test Signals
The primary signals are successful CMake configure/generate, successful build of `fdbserver_commitproxy`, and successful `fdbserver_commitproxylinktest`. Broader server and simulation tests that exercise commit proxy recruitment, transaction commit, conflict handling, and log-system integration validate that the target is linked with the needed runtime dependencies.
