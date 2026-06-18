# sources/storage-engines/wiredtiger/test/readonly/CMakeLists.txt

Purpose: build and register the readonly C test.

Important APIs and control flow: `create_test_executable(test_readonly SOURCES readonly.c EXECUTABLE_NAME "t" ADDITIONAL_FILES smoke.sh)` builds `readonly.c` as executable `t` and stages the smoke script. `add_test` runs the script from the binary directory. `set_tests_properties` labels the test `check`.

State and persistence behavior: CMake writes build-system metadata and the test executable. Runtime state is created by `readonly.c` and `smoke.sh`.

Dependencies and integration points: depends on the repository's `create_test_executable` helper and CTest. The short executable name is matched by `smoke.sh`.

Risks: if the executable name changes, the smoke script must change too. The test is POSIX-heavy, so platform gating must happen outside this file if required.

Test signals: `ctest -L check` should run `test_readonly` via `smoke.sh`.
