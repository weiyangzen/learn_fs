# sources/test-tools/ltp/testcases/kernel/syscalls/rt_tgsigqueueinfo/rt_tgsigqueueinfo01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rt_tgsigqueueinfo/rt_tgsigqueueinfo01.c` is a 181-line LTP source file in the `rt_tgsigqueueinfo` syscall test area. rt_tgsigqueueinfo targeted thread-group signal delivery coverage for self, parent-to-thread, and thread-to-thread paths. Source description: Author: Sumit Garg <sumit.garg@linaro.org>

## Important APIs, Types, and Functions

called APIs/macros: `rt_tgsigqueueinfo`, `SAFE_PTHREAD_CREATE`, `SAFE_PTHREAD_JOIN`, `SAFE_SIGACTION`, `TEST`, `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`; local functions: `sigusr1_handler`, `verify_signal_self`, `verify_signal_parent_thread`, `verify_signal_inter_thread`, `run`, `setup`; struct/table types referenced: `struct tcase`, `struct sigaction`, `struct tst_test`; important macros/constants: `_GNU_SOURCE`.

## Control Flow

Function-level flow is organized around `sigusr1_handler`, `verify_signal_self`, `verify_signal_parent_thread`, `verify_signal_inter_thread`, `run`, `setup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Some flow is concurrent: child processes or pthreads are used to exercise server, signal-delivery, or permission behavior, with waits/checkpoints joining the result. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is thread identity and pending signal delivery: pthread-created sender/receiver threads, gettid results, a SIGUSR1 sigaction with SA_SIGINFO, and volatile globals recording the received signum and sigval pointer.

## Dependencies and Integration Points

Direct includes: `<err.h>`, `<pthread.h>`, `"tst_safe_pthread.h"`, `"tst_test.h"`, `"lapi/syscalls.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.sa_flags`, `.sa_sigaction`, `.tcnt`, `.needs_checkpoints`, `.setup`, `.test`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

signal or child-process synchronization must avoid races

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `tst_safe_pthread.h`; `rt_tgsigqueueinfo failed`; `Test signal to self succeeded`; `Failed to deliver signal/data to self thread`; `Test signal to different thread succeeded`.
