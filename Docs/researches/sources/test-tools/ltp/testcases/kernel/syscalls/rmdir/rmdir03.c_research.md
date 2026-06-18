# sources/test-tools/ltp/testcases/kernel/syscalls/rmdir/rmdir03.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rmdir/rmdir03.c` is a 93-line LTP source file in the `rmdir` syscall test area. rmdir filesystem coverage for successful directory removal and error paths such as non-empty directories, loops, permissions, and read-only mounts.

## Important APIs, Types, and Functions

called APIs/macros: `rmdir`, `SAFE_GETPWNAM`, `SAFE_MKDIR`, `SAFE_SETEUID`, `TEST`; local functions: `do_rmdir`, `setup`, `cleanup`; struct/table types referenced: `struct testcase`, `struct passwd`, `struct tst_test`; important macros/constants: `DIR_MODE`, `NOEXCUTE_MODE`, `TESTDIR`, `TESTDIR2`, `TESTDIR3`, `TESTDIR4`.

## Control Flow

Function-level flow is organized around `do_rmdir`, `setup`, `cleanup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed. The test expects root privileges or temporarily changes credentials/capabilities.

## Dependencies and Integration Points

Direct includes: `<errno.h>`, `<sys/stat.h>`, `<sys/types.h>`, `<pwd.h>`, `<unistd.h>`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.setup`, `.cleanup`, `.tcnt`, `.test`, `.needs_root`, `.needs_tmpdir`.

## Risks and Edge Cases

permission cases depend on credentials, capabilities, and filesystem mode bits Explicit errno expectations include `EPERM`, `EACCES`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `rmdir() succeeded unexpectedly`; `rmdir() got expected errno`; `expected EPERM, but got`.
