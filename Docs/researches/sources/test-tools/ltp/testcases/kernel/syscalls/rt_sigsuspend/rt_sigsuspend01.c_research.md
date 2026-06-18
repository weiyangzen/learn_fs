# sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigsuspend/rt_sigsuspend01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigsuspend/rt_sigsuspend01.c` is a 63-line LTP source file in the `rt_sigsuspend` syscall test area. rt_sigsuspend coverage for EINTR wakeup and restoration of the process signal mask. Source description: Porting from Crackerjack to LTP is done by Manas Kumar Nayak maknayak@in.ibm.com> Waits for SIGALRM in rt_sigsuspend() then checks that process mask wasn't modified.

## Important APIs, Types, and Functions

called APIs/macros: `rt_sigsuspend`, `SAFE_RT_SIGACTION`, `SAFE_RT_SIGPROCMASK`, `TEST`; local functions: `sig_handler`, `verify_rt_sigsuspend`; struct/table types referenced: `struct sigaction`, `struct tst_test`.

## Control Flow

Function-level flow is organized around `sig_handler`, `verify_rt_sigsuspend`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is process/thread signal state: signal masks, handlers, pending signals, siginfo payloads, and thread ids.

## Dependencies and Integration Points

Direct includes: `<signal.h>`, `<errno.h>`, `"tst_test.h"`, `"lapi/syscalls.h"`, `"lapi/safe_rt_signal.h"`, `"lapi/signal.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.test_all`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

signal or child-process synchronization must avoid races Explicit errno expectations include `EINTR`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `lapi/safe_rt_signal.h`; `lapi/signal.h`; `sigemptyset failed`; `rt_sigsuspend() failed unexpectedly`; `signal mask not preserved`.
