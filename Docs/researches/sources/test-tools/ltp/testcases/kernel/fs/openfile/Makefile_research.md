# sources/test-tools/ltp/testcases/kernel/fs/openfile/Makefile

## Purpose

This Makefile builds the pthread-based simultaneous-open testcase.

## Important APIs, Types, and Functions

It includes `testcases.mk`, adds `LDLIBS += -lpthread`, and includes `generic_leaf_target.mk`.

## Control Flow

Generic LTP rules build the C source and link it with pthreads.

## State and Persistence Behavior

The Makefile owns no runtime state.

## Dependencies and Integration Points

Integrates `openfile.c` with the legacy LTP C framework and POSIX threads.

## Risks and Edge Cases

Missing `-lpthread` would break linkage. Toolchains using `-pthread` rather than `-lpthread` semantics may need framework support.

## Test Signals

Successful link of `openfile` with pthread symbols is the primary signal.
