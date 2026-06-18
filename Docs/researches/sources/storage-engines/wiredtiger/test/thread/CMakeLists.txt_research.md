# sources/storage-engines/wiredtiger/test/thread/CMakeLists.txt

## Purpose

This CMake file builds the WiredTiger threaded stress smoke-test executable and registers it with CTest.

## Important APIs, Types, and Functions

It calls `create_test_executable(test_thread SOURCES file.c rw.c stats.c t.c EXECUTABLE_NAME "t" ADDITIONAL_FILES smoke.sh)`, then registers `add_test(NAME test_thread COMMAND .../smoke.sh)` and labels it `check`.

## Control Flow

CMake builds the multi-source executable as `t`, copies `smoke.sh`, and CTest invokes the shell script, which runs row and variable table stress variants.

## State and Persistence Behavior

Build state is the `t` binary and copied smoke script. Runtime database directories are created by the executable.

## Dependencies and Integration Points

Integrates with the test utility library, CTest, the custom executable helper, and `smoke.sh` assumptions about the binary name.

## Risks and Edge Cases

The explicit executable name is part of the shell contract. Renaming without updating `smoke.sh` breaks the test.

## Test Signals

Signals are successful binary build and CTest execution of the four smoke commands in `smoke.sh`.
