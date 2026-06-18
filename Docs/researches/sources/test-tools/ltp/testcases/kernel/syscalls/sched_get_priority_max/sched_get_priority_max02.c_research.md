# sources/test-tools/ltp/testcases/kernel/syscalls/sched_get_priority_max/sched_get_priority_max02.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/sched_get_priority_max/sched_get_priority_max02.c` is a 26-line LTP source file in the `sched_get_priority_max` syscall test area. sched_get_priority_max scheduling-policy priority-range coverage for valid policies and invalid-policy EINVAL.

## Important APIs, Types, and Functions

called APIs/macros: `sched_get_priority_max`, `TST_EXP_FAIL`; local functions: `verif_sched_get_priority_max02`; struct/table types referenced: `struct tst_test`; important macros/constants: `SCHED_INVALID`.

## Control Flow

Function-level flow is organized around `verif_sched_get_priority_max02`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state.

## State and Persistence Behavior

State is process-local test state: descriptors, buffers, errno/TST_RET values, and temporary resources managed by the LTP harness.

## Dependencies and Integration Points

Direct includes: `<errno.h>`, `<sched.h>`, `"tst_test.h"`, `"lapi/syscalls.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.test_all`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

The main risk is errno drift or unsupported syscall behavior across architectures, kernel versions, and libc wrapper availability. Explicit errno expectations include `EINVAL`.

## Test Signals

TFAIL/TST_EXP_FAIL errno or invariant checks.
