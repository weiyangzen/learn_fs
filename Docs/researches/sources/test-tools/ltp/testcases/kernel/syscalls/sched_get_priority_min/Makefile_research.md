# sources/test-tools/ltp/testcases/kernel/syscalls/sched_get_priority_min/Makefile

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/sched_get_priority_min/Makefile` is the LTP leaf Makefile for the `sched_get_priority_min` syscall test directory. It connects the local tests to the common LTP syscall build rules so the cases in this directory are built and installed as part of the kernel syscall suite. Directory purpose: sched_get_priority_min scheduling-policy priority-range coverage for valid policies and invalid-policy EINVAL.

## Important APIs, Types, and Functions

This Makefile has no C APIs. It contributes make variables and include relationships. Notable build lines: `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

## Control Flow

Build flow is declarative: the LTP make recursion enters this directory, evaluates this file, then uses the included common rules to compile each C test in the folder. Any per-target flags here affect only the named local executable.

## State and Persistence Behavior

No runtime state or persistent data is owned by this file. Its state is build metadata: target-specific compiler flags, library links, or inclusion of shared LTP make rules.

## Dependencies and Integration Points

The integration point is the LTP build system under `testcases/kernel/syscalls`. It depends on the surrounding make include stack and on the C sources in the same directory.

## Risks and Edge Cases

Missing target-specific flags can silently break tests that need pthreads, realtime libraries, filesystem helpers, or generated syscall wrappers. Over-broad flags here would affect unrelated test binaries in the same directory.

## Test Signals

The signal is build/install coverage: the `sched_get_priority_min` tests compile through the LTP syscall build and any special targets receive their required flags.
