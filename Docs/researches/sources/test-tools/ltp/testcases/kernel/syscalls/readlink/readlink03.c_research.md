# sources/test-tools/ltp/testcases/kernel/syscalls/readlink/readlink03.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/readlink/readlink03.c` is a 121-line LTP source file in the `readlink` syscall test area. readlink coverage for symlink target reads, access through changed credentials, and pathname error handling. Source description: Ported to LTP: Wayne Boyer

## Important APIs, Types, and Functions

called APIs/macros: `readlink`, `SAFE_CHMOD`, `SAFE_GETPWNAM`, `SAFE_MKDIR`, `SAFE_SETEUID`, `SAFE_SYMLINK`, `SAFE_TOUCH`, `TEST`; local functions: `verify_readlink`, `setup`; struct/table types referenced: `struct tcase`, `struct passwd`, `struct tst_test`; important macros/constants: `DIR_TEMP`, `TEST_FILE1`, `SYM_FILE1`, `TEST_FILE2`, `SYM_FILE2`, `TEST_FILE3`, `SYM_FILE3`, `ELOOPFILE`, `TESTFILE`, `SYMFILE`.

## Control Flow

Function-level flow is organized around `verify_readlink`, `setup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed. The test expects root privileges or temporarily changes credentials/capabilities.

## Dependencies and Integration Points

Direct includes: `<pwd.h>`, `<errno.h>`, `<string.h>`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.tcnt`, `.test`, `.setup`, `.needs_tmpdir`, `.needs_root`.

## Risks and Edge Cases

bad-address cases are architecture and fault-path sensitive; permission cases depend on credentials, capabilities, and filesystem mode bits Explicit errno expectations include `EACCES`, `EINVAL`, `ENAMETOOLONG`, `ENOENT`, `ENOTDIR`, `ELOOP`, `EFAULT`, `ELOOPFILE`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `readlink() sueeeeded unexpectedly`; `readlink() failed unexpectedly; expected: %d - %s, got`; `readlink() failed as expected`.
