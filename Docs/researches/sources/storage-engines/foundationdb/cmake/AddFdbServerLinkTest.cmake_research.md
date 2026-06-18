# sources/storage-engines/foundationdb/cmake/AddFdbServerLinkTest.cmake

Purpose: This CMake helper defines reusable functions for FoundationDB server link tests and unit-test executables.

Important APIs and types: `add_fdbserver_link_test(target_name ...)` creates a Flow target using `fdbclient/LinkTest.cpp` and links the primary library with whole-archive semantics plus remaining libraries and `rapidxml`. `add_fdbserver_unit_test(target_name source_subdir ...)` creates an executable target using `fdbserver/FDBServerUnitTestMain.cpp`, sets `EXCLUDE_FROM_ALL`, defines `FDBSERVER_UNIT_TEST_SUITE`, and links similarly.

Control flow: Both functions treat the first variadic library argument as `primary_lib`, remove it from the list, compute a relative source path from the current source directory, create a target, then link with `$<LINK_LIBRARY:WHOLE_ARCHIVE,...>`.

State and persistence behavior: It creates CMake targets and compile definitions only; no runtime persistence.

Dependencies and integration points: It depends on the project `add_flow_target` macro, server/client test source files, whole-archive linker support through CMake generator expressions, and `rapidxml`.

Risks: Calls without at least one library will fail at `list(GET)`. Whole-archive behavior is linker/platform-sensitive. Unit-test suite selection depends on `source_subdir` matching registration in server unit-test code.

Test signals: Configure/build success for generated link-test and unit-test targets, correct source resolution, and successful link against whole-archived primary libraries are the key signals.
