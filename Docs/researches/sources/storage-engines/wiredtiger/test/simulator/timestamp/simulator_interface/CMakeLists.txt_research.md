# sources/storage-engines/wiredtiger/test/simulator/timestamp/simulator_interface/CMakeLists.txt

Purpose: builds the interactive timestamp simulator CLI frontend.

Important APIs and control flow: `add_executable(simulator_interface simulator_interface.cpp)` creates the tool, includes the local source directory, links `timestamp_simulator`, optionally links `wt::voidstar` under `ENABLE_ANTITHESIS`, and applies diagnostic flags.

State and persistence behavior: CMake produces the executable; runtime state is in the simulator library and process stdin/stdout.

Dependencies and integration points: depends on the timestamp simulator shared library and optional Antithesis target.

Risks: because this is an interactive executable, automated test coverage may only compile it unless explicit scripted input is provided.

Test signals: successful compile/link and manual or scripted CLI interactions that exercise timestamp rules.
