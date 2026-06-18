# sources/storage-engines/foundationdb/fdbserver/backupworker/CMakeLists.txt

## Purpose
This CMake file defines the `fdbserver_backupworker` static library and its basic link and unit-test targets.

## Important APIs and Build Rules
`fdb_find_sources(FDBSERVER_BACKUPWORKER_SRCS)` discovers source files in the directory. `add_flow_target(STATIC_LIBRARY NAME fdbserver_backupworker SRCS ${FDBSERVER_BACKUPWORKER_SRCS})` creates the library. `add_fdbserver_link_test()` creates a link test against `fdbserver_backupworker`, `fdbserver_logsystem`, and `fdbserver_core`. `add_fdbserver_unit_test()` creates the `backupworker` unit-test target with the same dependencies.

## Control Flow and Integration
The library receives common fdbserver include configuration through `configure_fdbserver_common_includes()`. Public include paths expose `backupworker/include`; private include paths expose the source directory. The library links privately to `fdbserver_core` and `fdbserver_logsystem`, matching the source files' use of backup interfaces, system keys, and log consumers.

## State, Risks, and Test Signals
The file has no runtime state. Build risk is mainly source discovery: new `.cpp` files in this directory join the static library automatically, so accidental test or experimental files can affect build and link behavior. The explicit link and unit-test targets are the main build-time signals that backup worker objects, including local `TEST_CASE`s, are linked.
