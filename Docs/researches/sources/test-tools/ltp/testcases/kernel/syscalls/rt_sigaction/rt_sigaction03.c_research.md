# sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigaction/rt_sigaction03.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigaction/rt_sigaction03.c` is a 146-line LTP source file in the `rt_sigaction` syscall test area. rt_sigaction signal handler ABI coverage for normal installs and invalid user pointers or sigset sizes. Source description: ***************************************************************************

## Important APIs, Types, and Functions

called APIs/macros: `ltp_rt_sigaction`, `TEST`; local functions: `cleanup`, `setup`, `handler`, `set_handler`, `main`; struct/table types referenced: `struct test_case_t`, `struct sigaction`; important macros/constants: `_GNU_SOURCE`, `INVAL_SIGSETSIZE`.

## Control Flow

Function-level flow is organized around `cleanup`, `setup`, `handler`, `set_handler`, `main`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. This file uses the older `test.h` harness: `main` parses options, loops over configured cases or signals, calls direct syscall wrappers, reports through `tst_resm`/`tst_brkm`, and exits through `tst_exit`. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is process/thread signal state: signal masks, handlers, pending signals, siginfo payloads, and thread ids.

## Dependencies and Integration Points

Direct includes: `<stdio.h>`, `<stdlib.h>`, `<unistd.h>`, `<signal.h>`, `<errno.h>`, `<sys/syscall.h>`, `<string.h>`, `"test.h"`, `"lapi/syscalls.h"`, `"lapi/rt_sigaction.h"`. Uses the older LTP `test.h` harness and legacy result macros. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

Legacy signal tests are ABI-sensitive: signal numbers, SIGSETSIZE, bad user pointers, and direct syscall wrappers can vary by architecture. Explicit errno expectations include `EINVAL`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `Signal Handler Called with signal number %d`; `Signal %d`; `%s failure with sig: %d as expected errno  = %s : %s`; `rt_sigaction call succeeded: result = %ld got error %d:but expected  %d`.
