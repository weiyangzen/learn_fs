# sources/test-tools/ltp/testcases/kernel/fs/proc/Makefile

## Purpose

This Makefile builds the `/proc` recursive read testcase.

## Important APIs, Types, and Functions

It includes `testcases.mk`, adds `LDLIBS += $(SELINUX_LIBS)`, and includes `generic_leaf_target.mk`.

## Control Flow

Generic LTP rules build `proc01.c`; SELinux libraries are linked when configured by the build system.

## State and Persistence Behavior

No runtime state is owned by the Makefile.

## Dependencies and Integration Points

Integrates optional SELinux-aware filtering in `proc01.c` with LTP configuration.

## Risks and Edge Cases

If SELinux headers are detected but `SELINUX_LIBS` is incomplete, link failure occurs. Without SELinux support, some LSM-specific known-issue filtering changes.

## Test Signals

Successful build with and without SELinux development support is the expected signal.
