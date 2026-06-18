# sources/storage-engines/wiredtiger/test/simulator/timestamp/call_log_manager/CMakeLists.txt

Purpose: builds the call-log replay frontend for the timestamp simulator.

Important APIs and control flow: `add_executable(call_log_manager call_log_manager.cpp)` creates the tool. Include directories expose the local directory and `test/3rdparty` for `nlohmann/json.hpp`. The executable links to `timestamp_simulator`, optionally links `wt::voidstar` when `ENABLE_ANTITHESIS` is set, and applies C++ diagnostic flags.

State and persistence behavior: produces an executable artifact. Runtime reads an external call-log file but CMake manages no state.

Dependencies and integration points: depends on the simulator library and bundled JSON library. Optional Antithesis integration is through `wt::voidstar`.

Risks: missing third-party JSON include path or shared-library runtime path will break the executable. Optional linking must stay aligned with Antithesis build configuration.

Test signals: the target should compile and link; a valid call log should replay through the built executable.
