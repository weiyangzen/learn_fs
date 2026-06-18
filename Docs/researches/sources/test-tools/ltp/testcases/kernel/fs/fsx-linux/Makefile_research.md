# sources/test-tools/ltp/testcases/kernel/fs/fsx-linux/Makefile

## Purpose

This Makefile builds the LTP rewrite of `fsx-linux`, a random file operation exerciser.

## Important APIs, Types, and Functions

It sets `top_srcdir`, includes `testcases.mk`, adds `CPPFLAGS += -DNO_XFS -I$(abs_srcdir) -D_LARGEFILE64_SOURCE -D_GNU_SOURCE`, sets `WCFLAGS += -w`, and includes `generic_leaf_target.mk`.

## Control Flow

The file delegates build/install flow to the LTP leaf target rules after setting compatibility flags.

## State and Persistence Behavior

No runtime state is owned by the Makefile. Build flags affect large-file and GNU API visibility.

## Dependencies and Integration Points

Integrates `fsx-linux.c` with the LTP C testcase framework. `-DNO_XFS` is retained for compatibility with historical fsx code, even though the rewritten source is generic.

## Risks and Edge Cases

`WCFLAGS += -w` suppresses warnings, so type or format issues can be missed at build time.

## Test Signals

Build success for the `fsx-linux` binary is the primary signal; warning-cleanliness is not enforced.
