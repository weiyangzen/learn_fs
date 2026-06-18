# sources/storage-engines/wiredtiger/test/manydbs/CMakeLists.txt

Purpose: build and register the `test_manydbs` executable.

Important behavior: `create_test_executable(test_manydbs SOURCES manydbs.c)` builds the binary. On Windows, CTest launches it through `powershell.exe $<TARGET_FILE:test_manydbs>` because the test has issues under the normal CTest process. Other platforms register `add_test(NAME test_manydbs COMMAND test_manydbs)`. The test is labeled `check`.

Control flow and state: CMake only declares build/test metadata and platform-specific launch behavior.

Dependencies and integration: relies on project test macros, the `WT_WIN` platform variable, and `manydbs.c`. It places the many-database condition-variable reset test in normal smoke coverage.

Risks and test signals: the platform wrapper hints at resource/process isolation sensitivity on Windows. A useful signal is cross-platform registration preserving the `check` label while still isolating Windows execution.
