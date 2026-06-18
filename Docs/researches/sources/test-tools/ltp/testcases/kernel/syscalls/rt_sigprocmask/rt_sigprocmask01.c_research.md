# sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigprocmask/rt_sigprocmask01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigprocmask/rt_sigprocmask01.c` is a 169-line LTP source file in the `rt_sigprocmask` syscall test area. rt_sigprocmask signal mask coverage for block/unblock/pending signal behavior and invalid argument handling. Source description: ***************************************************************************

## Important APIs, Types, and Functions

called APIs/macros: `ltp_rt_sigaction`, `rt_sigprocmask`, `TEST`; local functions: `cleanup`, `setup`, `sig_handler`, `main`; struct/table types referenced: `struct sigaction`; important macros/constants: `TEST_SIG`.

## Control Flow

Function-level flow is organized around `cleanup`, `setup`, `sig_handler`, `main`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. This file uses the older `test.h` harness: `main` parses options, loops over configured cases or signals, calls direct syscall wrappers, reports through `tst_resm`/`tst_brkm`, and exits through `tst_exit`. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is process/thread signal state: signal masks, handlers, pending signals, siginfo payloads, and thread ids.

## Dependencies and Integration Points

Direct includes: `<stdio.h>`, `<signal.h>`, `<errno.h>`, `"test.h"`, `"lapi/syscalls.h"`, `"lapi/rt_sigaction.h"`. Uses the older LTP `test.h` harness and legacy result macros. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

Signal-mask tests can be flaky if pending signals leak between iterations or if the direct rt_sigprocmask sigset size is wrong for the architecture.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `sigemptyset call failed`; `sigaddset call failed`; `rt_sigaction call failed`; `rt_sigprocmask call failed`; `call to kill() failed`.
