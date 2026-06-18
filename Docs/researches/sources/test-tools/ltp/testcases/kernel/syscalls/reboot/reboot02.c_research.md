# sources/test-tools/ltp/testcases/kernel/syscalls/reboot/reboot02.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/reboot/reboot02.c` is a 56-line LTP source file in the `reboot` syscall test area. reboot syscall coverage for permission, magic-number, and command validation without actually rebooting the test host. Source description: Author: Aniruddha Marathe <aniruddha.marathe@wipro.com>

## Important APIs, Types, and Functions

called APIs/macros: `reboot`, `SAFE_GETPWNAM`, `SAFE_SETEUID`, `TST_EXP_FAIL`; local functions: `run`; struct/table types referenced: `struct passwd`, `struct tcase`, `struct tst_test`; important macros/constants: `INVALID_CMD`, `CMD_DESC`.

## Control Flow

Function-level flow is organized around `run`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is process-local test state: descriptors, buffers, errno/TST_RET values, and temporary resources managed by the LTP harness. The test expects root privileges or temporarily changes credentials/capabilities.

## Dependencies and Integration Points

Direct includes: `<unistd.h>`, `<sys/reboot.h>`, `<linux/reboot.h>`, `<pwd.h>`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.needs_root`, `.test`, `.tcnt`.

## Risks and Edge Cases

permission cases depend on credentials, capabilities, and filesystem mode bits Explicit errno expectations include `EINVAL`, `EPERM`.

## Test Signals

TFAIL/TST_EXP_FAIL errno or invariant checks.
