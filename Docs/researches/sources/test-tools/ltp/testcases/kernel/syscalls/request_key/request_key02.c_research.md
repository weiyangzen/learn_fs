# sources/test-tools/ltp/testcases/kernel/syscalls/request_key/request_key02.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/request_key/request_key02.c` is a 83-line LTP source file in the `request_key` syscall test area. request_key/keyring syscall coverage for key lookup, destination keyrings, permissions, regressions, and invalid argument errors. Source description: Author: Xiao Yang <yangx.jy@cn.fujitsu.com>

## Important APIs, Types, and Functions

called APIs/macros: `request_key`, `keyctl`, `TST_EXP_FAIL2`; local functions: `verify_request_key`, `init_key`, `setup`; struct/table types referenced: `struct test_case`, `struct tst_test`.

## Control Flow

Function-level flow is organized around `verify_request_key`, `init_key`, `setup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is kernel keyring state: session keyrings, user keys, permissions, request destination policy, and child-process attempts to trigger request_key behavior. Keys are transient kernel objects scoped to the test session.

## Dependencies and Integration Points

Direct includes: `<errno.h>`, `"tst_test.h"`, `"lapi/keyctl.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.setup`, `.tcnt`, `.test`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

Keyring tests depend on kernel keyring support, capability and permission semantics, and historical CVE fixes. Some cases deliberately stress failure paths that could hang or crash buggy kernels. Explicit errno expectations include `ENOKEY`, `EKEYREVOKED`, `EKEYEXPIRED`.

## Test Signals

TFAIL/TST_EXP_FAIL errno or invariant checks; TBROK for fixture/setup failures; notable reported messages include `lapi/keyctl.h`; `keyring`; `request_key(\`; `add_key() failed`; `failed to revoke a key`.
