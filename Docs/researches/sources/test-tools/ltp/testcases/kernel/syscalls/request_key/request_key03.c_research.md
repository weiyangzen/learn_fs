# sources/test-tools/ltp/testcases/kernel/syscalls/request_key/request_key03.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/request_key/request_key03.c` is a 228-line LTP source file in the `request_key` syscall test area. request_key/keyring syscall coverage for key lookup, destination keyrings, permissions, regressions, and invalid argument errors.

## Important APIs, Types, and Functions

called APIs/macros: `request_key`, `keyctl`, `SAFE_FORK`, `SAFE_WAITPID`, `TEST`; local functions: `run_child_add`, `run_child_request`, `do_test`; struct/table types referenced: `struct test_case`, `struct tst_test`, `struct tst_option`, `struct tst_tag`.

## Control Flow

Function-level flow is organized around `run_child_add`, `run_child_request`, `do_test`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Some flow is concurrent: child processes or pthreads are used to exercise server, signal-delivery, or permission behavior, with waits/checkpoints joining the result. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is kernel keyring state: session keyrings, user keys, permissions, request destination policy, and child-process attempts to trigger request_key behavior. Keys are transient kernel objects scoped to the test session.

## Dependencies and Integration Points

Direct includes: `<errno.h>`, `<stdbool.h>`, `<stdlib.h>`, `<sys/wait.h>`, `"tst_test.h"`, `"lapi/keyctl.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.test`, `.tcnt`, `.forks_child`, `.runtime`, `.options`, `.tags`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

Keyring tests depend on kernel keyring support, capability and permission semantics, and historical CVE fixes. Some cases deliberately stress failure paths that could hang or crash buggy kernels. Explicit errno expectations include `EINVAL`, `ENOKEY`, `EDQUOT`, `ENOENT`, `ENODEV`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; TCONF for unsupported kernel, filesystem, or feature combinations; TBROK for fixture/setup failures; notable reported messages include `lapi/keyctl.h`; `unexpected error adding key of type '%s'`; `unable to clear keyring`; `add_key() process runtime exceeded`; `unexpected error requesting key of type '%s'`.
