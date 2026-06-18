## sources/storage-engines/foundationdb/bindings/flow/tester/CMakeLists.txt

Purpose: build definition for the Flow binding tester executable.

Important targets: `TEST_SRCS` lists `DirectoryTester.cpp`, `Tester.cpp`, and `Tester.h`. `add_flow_target(EXECUTABLE NAME fdb_flow_tester ...)` builds the tester, and `target_link_libraries(fdb_flow_tester fdb_flow)` links it to the Flow binding library.

Control flow: included from the parent Flow CMake file via `add_subdirectory(tester)`.

State and persistence: only build artifacts; no runtime state in this file.

Dependencies and integration points: depends on parent include directories and `fdb_flow` target.

Risks: tester source additions must be reflected here. Missing link dependencies would surface as build failures.

Test signals: building this target validates tester integration with the library.
