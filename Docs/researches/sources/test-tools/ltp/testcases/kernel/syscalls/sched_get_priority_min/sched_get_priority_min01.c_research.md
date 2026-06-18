# sources/test-tools/ltp/testcases/kernel/syscalls/sched_get_priority_min/sched_get_priority_min01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/sched_get_priority_min/sched_get_priority_min01.c` is a 47-line LTP source file in the `sched_get_priority_min` syscall test area. sched_get_priority_min scheduling-policy priority-range coverage for valid policies and invalid-policy EINVAL.

## Important APIs, Types, and Functions

called APIs/macros: `sched_get_priority_min`, `TST_EXP_VAL`; local functions: `run_test`; struct/table types referenced: `struct test_case`, `struct tst_test`; important macros/constants: `_GNU_SOURCE`, `POLICY_DESC`.

## Control Flow

Function-level flow is organized around `run_test`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is process-local test state: descriptors, buffers, errno/TST_RET values, and temporary resources managed by the LTP harness.

## Dependencies and Integration Points

Direct includes: `<sched.h>`, `"tst_test.h"`, `"lapi/sched.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.tcnt`, `.test`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

The main risk is errno drift or unsupported syscall behavior across architectures, kernel versions, and libc wrapper availability.

## Test Signals

notable reported messages include `lapi/sched.h`.
