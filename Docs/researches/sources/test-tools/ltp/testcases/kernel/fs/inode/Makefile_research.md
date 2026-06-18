# sources/test-tools/ltp/testcases/kernel/fs/inode/Makefile

## Purpose

This Makefile builds the `inode01` and `inode02` filesystem tree generation tests.

## Important APIs, Types, and Functions

It sets `top_srcdir`, includes `testcases.mk`, adds `CPPFLAGS += -DLINUX`, and includes `generic_leaf_target.mk`.

## Control Flow

The file delegates target discovery and build/install behavior to the LTP generic leaf rules after setting the `LINUX` compile define.

## State and Persistence Behavior

No runtime state is owned. The `LINUX` define enables Linux-specific include/prototype paths in the C sources.

## Dependencies and Integration Points

Integrates the legacy `inode01.c` and `inode02.c` tests with LTP's C testcase framework.

## Risks and Edge Cases

If the C files are modernized to stop using `#ifdef LINUX`, this flag may become unnecessary; until then, removing it can break prototypes and includes.

## Test Signals

Successful build of both inode testcase binaries is the main signal.
