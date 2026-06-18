# sources/storage-engines/foundationdb/fdbserver/sequencer/CMakeLists.txt

Purpose: defines the `fdbserver_sequencer` static library and its build validation.

Important APIs and functions: source discovery uses `fdb_find_sources`. `add_flow_target` creates the library. Link and unit tests validate against `fdbserver_core`. Common include setup exports the `include` directory publicly and the local directory privately. `target_link_libraries` records the core dependency.

Control flow, state, and persistence: CMake metadata only; no runtime state.

Dependencies and integration: integrates sequencer/master code into the fdbserver build. The public include path exposes `MasterServer.h` while local files such as `MasterData.h` remain implementation details.

Risks and test signals: risks are missing new source files, absent core linkage, or public include path breakage. Build and unit-test target success are the primary signals.
