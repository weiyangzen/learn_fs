# sources/storage-engines/wiredtiger/bench/dhandle/CMakeLists.txt

## Purpose
This CMake file registers the data-handle benchmark executable when building on POSIX platforms.

## Important APIs, Types, and Functions
It calls `project(C)`, includes `test/ctest_helpers.cmake`, gates on `WT_POSIX`, and invokes `create_test_executable(bench_dhandle SOURCES bench_dhandle.c bench_timer.c)`.

## Control Flow, State, and Dependencies
During configure, non-POSIX builds skip the target. POSIX builds create a benchmark/test executable linked according to repository helper rules. Dependencies are the benchmark C files and test utility infrastructure.

## Integration Points, Risks, and Test Signals
It integrates the dhandle benchmark into the top-level `add_subdirectory(bench/dhandle)`. Risk is no target on Windows by design. Signal is generated `bench_dhandle` target in POSIX builds.
