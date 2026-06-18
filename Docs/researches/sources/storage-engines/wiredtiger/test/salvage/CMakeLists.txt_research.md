# sources/storage-engines/wiredtiger/test/salvage/CMakeLists.txt

Purpose: build and register the salvage C test with CTest.

Important APIs and control flow: `create_test_executable(test_salvage SOURCES salvage.c)` builds the executable. `add_test(NAME test_salvage COMMAND test_salvage)` registers it directly. `set_tests_properties(... LABELS "check")` includes it in check smoke runs.

State and persistence behavior: build metadata and executable are produced by CMake. Runtime creates and destroys `WT_TEST` files.

Dependencies and integration points: depends on the repository CMake test helper and CTest. It does not stage a wrapper script.

Risks: the direct command assumes the executable is discoverable in the CTest working context established by the helper macro.

Test signals: `ctest -R test_salvage` or `ctest -L check` should execute the compiled program successfully.
