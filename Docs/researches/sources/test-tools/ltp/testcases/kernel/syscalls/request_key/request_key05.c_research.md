# sources/test-tools/ltp/testcases/kernel/syscalls/request_key/request_key05.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/request_key/request_key05.c` is a 40-line LTP source file in the `request_key` syscall test area. request_key/keyring syscall coverage for key lookup, destination keyrings, permissions, regressions, and invalid argument errors.

## Important APIs, Types, and Functions

called APIs/macros: `request_key`; local functions: `run`; struct/table types referenced: `struct tst_test`, `struct tst_tag`; important macros/constants: `ATTEMPTS`.

## Control Flow

Function-level flow is organized around `run`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is kernel keyring state: session keyrings, user keys, permissions, request destination policy, and child-process attempts to trigger request_key behavior. Keys are transient kernel objects scoped to the test session.

## Dependencies and Integration Points

Direct includes: `<unistd.h>`, `<sys/syscall.h>`, `"tst_test.h"`, `"lapi/syscalls.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.test_all`, `.tags`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

Keyring tests depend on kernel keyring support, capability and permission semantics, and historical CVE fixes. Some cases deliberately stress failure paths that could hang or crash buggy kernels.

## Test Signals

TPASS/TST_EXP_PASS success reports; notable reported messages include `Requesting dead key`.
