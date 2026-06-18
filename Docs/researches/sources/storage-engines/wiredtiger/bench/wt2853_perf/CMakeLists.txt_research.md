# sources/storage-engines/wiredtiger/bench/wt2853_perf/CMakeLists.txt

## Purpose
This CMake file wires the WT-2853 performance regression test into the WiredTiger build.

## Important APIs, Types, and Functions
It checks `WT_POSIX` and returns early on non-POSIX systems. On supported platforms it calls `create_test_executable(test_wt2853_perf SOURCES main.c)`.

## Control Flow
Configure-time logic skips the target on Windows/non-POSIX builds. Otherwise, the test executable is compiled from `main.c` using repository CMake helper macros.

## State and Persistence Behavior
No runtime state is managed here. It affects generated build files and whether the test binary exists.

## Dependencies and Integration Points
It depends on the repository's CMake helper `create_test_executable`, POSIX support, and `main.c`. The companion `smoke.sh` expects the resulting binary name `test_wt2853_perf`.

## Risks and Edge Cases
The early return means CI coverage is platform-dependent. If helper macro behavior or binary naming changes, `smoke.sh` can drift from the build target.

## Test Signals
CMake configure/build on POSIX should produce `test_wt2853_perf`; non-POSIX configure should skip it without error. `smoke.sh` validates row and column table modes.
