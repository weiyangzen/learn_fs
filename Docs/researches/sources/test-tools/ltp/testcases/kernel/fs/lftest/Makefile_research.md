# sources/test-tools/ltp/testcases/kernel/fs/lftest/Makefile

## Purpose

This Makefile builds the `lftest` large-file seek/write testcase.

## Important APIs, Types, and Functions

It includes `testcases.mk`, adds `CPPFLAGS += -D_FILE_OFFSET_BITS=64 -D_LARGEFILE_SOURCE`, and includes `generic_leaf_target.mk`.

## Control Flow

The LTP generic leaf rules build the local C testcase with large-file API remapping enabled.

## State and Persistence Behavior

The Makefile owns no runtime state. Compile flags make standard `off_t` operations large-file-capable.

## Dependencies and Integration Points

Integrates `lftest.c` with the LTP C framework.

## Risks and Edge Cases

Removing the large-file flags weakens the purpose of the test on 32-bit platforms.

## Test Signals

Build success with large-file flags is the expected signal.
