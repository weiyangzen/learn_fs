# sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigqueueinfo/rt_sigqueueinfo02.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigqueueinfo/rt_sigqueueinfo02.c` is a 97-line LTP source file in the `rt_sigqueueinfo` syscall test area. rt_sigqueueinfo signal delivery coverage for siginfo payloads, threads, and invalid pid/signal/permission cases. Source description: Author: Ma Xinjian <maxj.fnst@fujitsu.com>

## Important APIs, Types, and Functions

called APIs/macros: `rt_sigqueueinfo`, `SAFE_FORK`, `SAFE_WAITPID`, `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`, `TST_EXP_FAIL`, `TST_TEST_TCONF`; local functions: `setup`, `parent_do`, `child_do`, `verify_rt_sigqueueinfo`; struct/table types referenced: `struct test_case_t`, `struct tst_test`, `struct tst_buffers`.

## Control Flow

Function-level flow is organized around `setup`, `parent_do`, `child_do`, `verify_rt_sigqueueinfo`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Some flow is concurrent: child processes or pthreads are used to exercise server, signal-delivery, or permission behavior, with waits/checkpoints joining the result. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is process/thread signal state: signal masks, handlers, pending signals, siginfo payloads, and thread ids.

## Dependencies and Integration Points

Direct includes: `<pwd.h>`, `<signal.h>`, `"config.h"`, `"tst_test.h"`, `"rt_sigqueueinfo.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.setup`, `.tcnt`, `.test`, `.forks_child`, `.needs_checkpoints`, `.bufs`. Compile-time feature guards gate optional kernel/libc interfaces.

## Risks and Edge Cases

permission cases depend on credentials, capabilities, and filesystem mode bits; signal or child-process synchronization must avoid races Explicit errno expectations include `EINVAL`, `EPERM`, `ESRCH`.

## Test Signals

TFAIL/TST_EXP_FAIL errno or invariant checks; TCONF for unsupported kernel, filesystem, or feature combinations; notable reported messages include `no thread group matching tgid is found`; `This system does not support rt_sigqueueinfo()`.
