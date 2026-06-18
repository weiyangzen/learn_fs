# sources/test-tools/ltp/testcases/kernel/syscalls/sched_getaffinity/sched_getaffinity01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/sched_getaffinity/sched_getaffinity01.c` is a 96-line LTP source file in the `sched_getaffinity` syscall test area. sched_getaffinity CPU-mask coverage for valid masks and EFAULT/EINVAL/ESRCH error behavior. Source description: Description: This case tests the sched_getaffinity() syscall History:     Porting from Crackerjack to LTP is done by Manas Kumar Nayak maknayak@in.ibm.com>

## Important APIs, Types, and Functions

called APIs/macros: `sched_getaffinity`, `SAFE_SYSCONF`, `TEST`; local functions: `errno_test`, `do_test`, `setup`; struct/table types referenced: `struct tst_test`; important macros/constants: `_GNU_SOURCE`.

## Control Flow

Function-level flow is organized around `errno_test`, `do_test`, `setup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is the process program break and virtual address space. The tests do not persist data beyond the process lifetime.

## Dependencies and Integration Points

Direct includes: `<errno.h>`, `<sched.h>`, `<stdlib.h>`, `<string.h>`, `"tst_test.h"`, `"tst_safe_macros.h"`, `"lapi/cpuset.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.setup`, `.test_all`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

bad-address cases are architecture and fault-path sensitive Explicit errno expectations include `EINVAL`, `EFAULT`, `ESRCH`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; TBROK for fixture/setup failures; notable reported messages include `sched_getaffinity() returned %ld, expected -1`; `sched_getaffinity() should fail with %s`; `sched_getaffinity() failed`; `fail to get cpu affinity`.
