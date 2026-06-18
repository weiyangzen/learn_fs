# sources/storage-engines/foundationdb/documentation/tutorial/CMakeLists.txt

## Purpose
Builds Flow tutorial and exercise executables for FoundationDB documentation examples.

## Important APIs, Types, and Functions
Uses `add_flow_target(EXECUTABLE ...)` to create `tutorial`, `print_in_order`, `make_h2o`, `dining_philosophers`, `play`, and `play_network`. Each target links `fdbclient`.

## Control Flow
CMake defines a source variable for each executable, invokes `add_flow_target`, then calls `target_link_libraries`. There is no conditional logic.

## State and Persistence Behavior
Creates build-system state and generated executable artifacts. Actor-compiler outputs live in the build tree.

## Dependencies and Integration Points
Depends on FoundationDB CMake helpers, actor compiler integration, and the `fdbclient` target. Integrates with `.actor.cpp` tutorial sources.

## Risks
Breakage in `add_flow_target` affects every tutorial binary. Examples that only need Flow still inherit `fdbclient`. No tests are registered here.

## Test Signals
Build all six targets and smoke run finite examples such as `play`, `print_in_order`, and selected `tutorial` actors; manually test client/server binaries.
