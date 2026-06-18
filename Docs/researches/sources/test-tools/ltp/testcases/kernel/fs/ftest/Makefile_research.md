# sources/test-tools/ltp/testcases/kernel/fs/ftest/Makefile

## Purpose

This Makefile builds the `ftest01` through `ftest08` legacy filesystem stress binaries and their shared helper object.

## Important APIs, Types, and Functions

It includes `testcases.mk`, sets `FILTER_OUT_MAKE_TARGETS := libftest`, includes `generic_leaf_target.mk`, and adds `$(MAKE_TARGETS): %: libftest.o` so every testcase links with the helper object.

## Control Flow

Generic LTP leaf rules discover C targets; the custom dependency ensures test binaries link against `libftest.o` while not trying to install/build `libftest` as a standalone testcase.

## State and Persistence Behavior

The Makefile owns no runtime state. Build state includes `libftest.o` and each testcase executable.

## Dependencies and Integration Points

Integrates all local `ftest*.c` files with `libftest.c`/`libftest.h` and the legacy LTP `test.h` API.

## Risks and Edge Cases

If new helper-only sources are added, they must be filtered similarly. If a testcase stops using `libftest.o`, the unconditional dependency still links it.

## Test Signals

Successful compilation and linkage of every `ftestNN` binary with `libftest.o` are the expected signals.
