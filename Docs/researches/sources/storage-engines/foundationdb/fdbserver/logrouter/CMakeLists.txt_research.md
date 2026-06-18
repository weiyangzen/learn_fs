# sources/storage-engines/foundationdb/fdbserver/logrouter/CMakeLists.txt

## Purpose
This CMake file builds the FoundationDB log router static library and validates its link dependencies.

## Important APIs, Types, And Functions
It calls `fdb_find_sources(FDBSERVER_LOGROUTER_SRCS)`, creates `fdbserver_logrouter` with `add_flow_target(STATIC_LIBRARY ...)`, adds `fdbserver_logrouterlinktest`, configures common fdbserver includes, exposes the local `include` directory publicly, and links privately against `fdbserver_core` and `fdbserver_logsystem`.

## Control Flow
CMake discovers sources in the directory, constructs the static library, configures include paths, and adds a link test that pulls in log router, logsystem, and core libraries.

## State And Persistence Behavior
There is no runtime state. Build artifacts are static library outputs and link-test targets.

## Dependencies And Integration Points
The target exports headers from `fdbserver/logrouter/include` and depends on core worker/TLog types plus logsystem consumer logic used by `LogRouter.cpp`.

## Risks And Test Signals
Missing dependencies may surface only at link-test time because the source uses many actor/logsystem symbols. Build tests should ensure the static library and `fdbserver_logrouterlinktest` build after source or include changes.
