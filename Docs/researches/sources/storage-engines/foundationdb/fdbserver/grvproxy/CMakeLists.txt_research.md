# sources/storage-engines/foundationdb/fdbserver/grvproxy/CMakeLists.txt

## Purpose
Defines the GRV proxy component as a static library and wires it into FoundationDB link and unit-test targets.

## Important APIs, Types, and Functions
- `fdb_find_sources(FDBSERVER_GRVPROXY_SRCS)` discovers sources.
- `add_flow_target(STATIC_LIBRARY NAME fdbserver_grvproxy ...)` builds the library.
- `add_fdbserver_link_test` validates linkability with `fdbserver_logsystem` and `fdbserver_core`.
- `add_fdbserver_unit_test(fdbserver_grvproxy_test grvproxy ...)` registers GRV proxy tests.
- `configure_fdbserver_common_includes`, `target_include_directories`, and `target_link_libraries` define include visibility and dependencies.

## Control Flow
CMake discovers sources, builds `fdbserver_grvproxy`, adds link/unit-test targets, exposes `include/` publicly, keeps the source directory private, and links core/logsystem dependencies.

## State and Persistence Behavior
No runtime state; it only affects build graph state.

## Dependencies and Integration Points
Depends on `fdbserver_core` and `fdbserver_logsystem`, matching the GRV proxy runtime dependency on knobs, worker interfaces, and log-system committed-version confirmation.

## Risks and Edge Cases
Automatic source discovery can include new files without explicit review. Only `include/` is public, so private helper headers remain component-local.

## Test Signals
Registers both a link test and the `grvproxy` unit-test target.
