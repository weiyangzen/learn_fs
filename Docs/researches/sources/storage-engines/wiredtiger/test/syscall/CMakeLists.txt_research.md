# sources/storage-engines/wiredtiger/test/syscall/CMakeLists.txt

## Purpose

This CMake file builds and registers the WiredTiger syscall trace test suite. It creates the base executable used by `.run` trace specifications and registers `syscall.py` as a CTest test.

## Important APIs, Types, and Functions

It calls `create_test_executable(test_wt2336_base SOURCES wt2336_base/main.c ADDITIONAL_FILES syscall.py ADDITIONAL_DIRECTORIES wt2336_base)`, `add_test(NAME test_syscall COMMAND python3 .../syscall.py)`, and sets `SKIP_RETURN_CODE 3`.

## Control Flow

At configure/build time, CMake builds the executable and copies the runner and test directory. At test time, CTest invokes the Python runner, which discovers `.run` files and compares system-call traces.

## State and Persistence Behavior

The build tree receives the executable, copied runner, and copied syscall test directories. Runtime scratch directories are managed by `syscall.py`.

## Dependencies and Integration Points

Integrates with WiredTiger's custom `create_test_executable` helper, CTest, Python 3, and environment-error skip semantics from the runner.

## Risks and Edge Cases

The skip return code is significant: runner exit code 3 is treated as an environment skip, not failure. Missing copied files or mismatched executable naming would prevent discovery.

## Test Signals

Signals are successful build of `test_wt2336_base` and a CTest `test_syscall` result of pass or skip-on-environment.
