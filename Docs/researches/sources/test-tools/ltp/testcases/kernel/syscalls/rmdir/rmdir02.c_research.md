# sources/test-tools/ltp/testcases/kernel/syscalls/rmdir/rmdir02.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rmdir/rmdir02.c` is a 110-line LTP source file in the `rmdir` syscall test area. rmdir filesystem coverage for successful directory removal and error paths such as non-empty directories, loops, permissions, and read-only mounts. Source description: Ported to LTP: Wayne Boyer

## Important APIs, Types, and Functions

called APIs/macros: `rmdir`, `SAFE_MKDIR`, `SAFE_SYMLINK`, `SAFE_TOUCH`, `TEST`; local functions: `setup`, `verify_rmdir`; struct/table types referenced: `struct testcase`, `struct tst_test`; important macros/constants: `DIR_MODE`, `FILE_MODE`, `TESTDIR`, `TESTDIR2`, `TESTDIR3`, `TESTDIR4`, `MNT_POINT`, `TESTDIR5`, `TESTFILE`, `TESTFILE2`.

## Control Flow

Function-level flow is organized around `setup`, `verify_rmdir`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed. The test expects root privileges or temporarily changes credentials/capabilities. It integrates with LTP device mounting or filesystem-matrix execution.

## Dependencies and Integration Points

Direct includes: `<errno.h>`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.setup`, `.tcnt`, `.test`, `.needs_root`, `.needs_rofs`, `.mntpoint`.

## Risks and Edge Cases

bad-address cases are architecture and fault-path sensitive; filesystem-specific behavior can require TCONF gating Explicit errno expectations include `ENOTEMPTY`, `ENAMETOOLONG`, `ENOENT`, `ENOTDIR`, `EFAULT`, `ELOOP`, `EROFS`, `EBUSY`, `EINVAL`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `rmdir() succeeded unexpectedly (%li)`; `rmdir() failed as expected`; `rmdir() failed unexpectedly; expected: %d - %s`.
