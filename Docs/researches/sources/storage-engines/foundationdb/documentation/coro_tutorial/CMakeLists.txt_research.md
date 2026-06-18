# sources/storage-engines/foundationdb/documentation/coro_tutorial/CMakeLists.txt

## Purpose
This one-line CMake file registers the coroutine tutorial executable and links it against `fdbclient`.

## Important APIs, Types, And Functions
It calls `add_flow_target(EXECUTABLE NAME coro_tutorial SRCS tutorial.cpp)` and `target_link_libraries(coro_tutorial PUBLIC fdbclient)`.

## Control Flow
During the documentation CMake traversal, this subdirectory defines the `coro_tutorial` target from `tutorial.cpp`, then attaches the FoundationDB client library.

## State And Persistence
It creates build-system target metadata only. No runtime persistence is involved.

## Dependencies And Integration Points
It depends on the FoundationDB build's `add_flow_target` helper and the `fdbclient` target. It integrates the coroutine tutorial into the normal CMake build graph.

## Risks
The file assumes `add_flow_target` is already in scope. Since the source uses Flow, RPC, and FDB client APIs, link or compile failures can appear here if those target dependencies are incomplete or if coroutine support flags are not propagated by `add_flow_target`.

## Test Signals
The main signal is a successful build of the `coro_tutorial` target.
