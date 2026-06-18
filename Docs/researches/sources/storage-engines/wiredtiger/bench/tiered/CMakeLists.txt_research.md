# sources/storage-engines/wiredtiger/bench/tiered/CMakeLists.txt

## Purpose
This CMake file registers the tiered-storage push/pull benchmark executable.

## Important APIs, Types, and Functions
It calls `create_test_executable(test_push_pull SOURCES push_pull.c)`.

## Control Flow, State, and Dependencies
During configure, the repository test helper creates a `test_push_pull` target from `push_pull.c`. It depends on the top-level inclusion of ctest helpers and WiredTiger test utility link rules.

## Integration Points, Risks, and Test Signals
It integrates the tiered benchmark into the top-level benchmark suite. Risk is minimal; build failure indicates missing helper setup or source compile problems. Signal is the generated executable target.
