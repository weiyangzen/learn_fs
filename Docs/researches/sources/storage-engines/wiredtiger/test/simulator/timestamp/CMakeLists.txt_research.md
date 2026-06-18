# sources/storage-engines/wiredtiger/test/simulator/timestamp/CMakeLists.txt

Purpose: builds the shared timestamp simulator library and delegates front-end executable targets.

Important APIs and control flow: `add_library(timestamp_simulator SHARED ...)` compiles `connection_simulator.cpp`, `session_simulator.cpp`, and `timestamp_manager.cpp`. It exposes `src/include`, compiles as C++17, applies diagnostic flags, then adds `call_log_manager` and `simulator_interface` subdirectories.

State and persistence behavior: produces a shared library artifact; no runtime state is handled in CMake.

Dependencies and integration points: downstream executables link to `timestamp_simulator`. The target depends on repository diagnostic flag variables and compiler support for C++17.

Risks: simulator headers are public to consumers, so include path and ABI changes affect both frontends. A shared library is produced even though the tools are test utilities, which can matter for runtime library lookup.

Test signals: successful build of `timestamp_simulator`, `call_log_manager`, and `simulator_interface` validates the CMake integration.
