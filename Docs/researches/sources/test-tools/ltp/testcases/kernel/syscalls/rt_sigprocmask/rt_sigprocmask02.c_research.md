# sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigprocmask/rt_sigprocmask02.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigprocmask/rt_sigprocmask02.c` is a 123-line LTP source file in the `rt_sigprocmask` syscall test area. rt_sigprocmask signal mask coverage for block/unblock/pending signal behavior and invalid argument handling. Source description: ***************************************************************************

## Important APIs, Types, and Functions

called APIs/macros: `rt_sigprocmask`, `TEST`; local functions: `cleanup`, `setup`, `main`; struct/table types referenced: `struct test_case_t`.

## Control Flow

Function-level flow is organized around `cleanup`, `setup`, `main`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. This file uses the older `test.h` harness: `main` parses options, loops over configured cases or signals, calls direct syscall wrappers, reports through `tst_resm`/`tst_brkm`, and exits through `tst_exit`. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is process/thread signal state: signal masks, handlers, pending signals, siginfo payloads, and thread ids.

## Dependencies and Integration Points

Direct includes: `<stdio.h>`, `<signal.h>`, `<errno.h>`, `"test.h"`, `"lapi/syscalls.h"`, `"tso_signal.h"`. Uses the older LTP `test.h` harness and legacy result macros. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

Signal-mask tests can be flaky if pending signals leak between iterations or if the direct rt_sigprocmask sigset size is wrong for the architecture. Explicit errno expectations include `EINVAL`, `EFAULT`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `tso_signal.h`; `Call to sigfillset() failed.`; `but should failed`; `Got expected errno`; `Got unexpected errno`.
