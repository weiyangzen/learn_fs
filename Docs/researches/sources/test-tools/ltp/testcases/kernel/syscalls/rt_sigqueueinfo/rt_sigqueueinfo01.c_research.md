# sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigqueueinfo/rt_sigqueueinfo01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigqueueinfo/rt_sigqueueinfo01.c` is a 116-line LTP source file in the `rt_sigqueueinfo` syscall test area. rt_sigqueueinfo signal delivery coverage for siginfo payloads, threads, and invalid pid/signal/permission cases. Source description: Author: Christian Amann <camann@suse.com>

## Important APIs, Types, and Functions

called APIs/macros: `rt_sigqueueinfo`, `SAFE_MALLOC`, `SAFE_PTHREAD_CREATE`, `SAFE_PTHREAD_JOIN`, `TEST`, `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`, `TST_TEST_TCONF`; local functions: `received_signal`, `verify_sigqueueinfo`, `setup`, `cleanup`; struct/table types referenced: `struct sigaction`, `struct tst_test`; important macros/constants: `SIGNAL`, `DATA`.

## Control Flow

Function-level flow is organized around `received_signal`, `verify_sigqueueinfo`, `setup`, `cleanup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Some flow is concurrent: child processes or pthreads are used to exercise server, signal-delivery, or permission behavior, with waits/checkpoints joining the result.

## State and Persistence Behavior

State is process/thread signal state: signal masks, handlers, pending signals, siginfo payloads, and thread ids.

## Dependencies and Integration Points

Direct includes: `<signal.h>`, `<stdlib.h>`, `"config.h"`, `"tst_test.h"`, `"tst_safe_pthread.h"`, `"rt_sigqueueinfo.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.test_all`, `.setup`, `.cleanup`, `.needs_checkpoints`. Compile-time feature guards gate optional kernel/libc interfaces.

## Risks and Edge Cases

signal or child-process synchronization must avoid races

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; TCONF for unsupported kernel, filesystem, or feature combinations; TBROK for fixture/setup failures; notable reported messages include `tst_safe_pthread.h`; `Received correct signal and data!`; `Received wrong signal and/or data!`; `Signal handling went wrong!`; `Failed to set sigaction for handler thread!`.
