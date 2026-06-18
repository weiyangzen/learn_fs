# sources/test-tools/ltp/testcases/kernel/syscalls/renameat/renameat01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/renameat/renameat01.c` is a 245-line LTP source file in the `renameat` syscall test area. renameat dirfd-relative filesystem rename coverage for success and descriptor/path error behavior. Source description: Author: Yi Yang <yyangcdl@cn.ibm.com>

## Important APIs, Types, and Functions

called APIs/macros: `renameat`, `SAFE_MKDIR`, `SAFE_MOUNT`, `SAFE_OPEN`, `SAFE_SYMLINK`, `SAFE_TOUCH`, `TEST`; local functions: `setup`, `cleanup`, `renameat_verify`, `main`; struct/table types referenced: `struct test_case_t`; important macros/constants: `_GNU_SOURCE`, `MNTPOINT`, `TESTDIR`, `NEW_TESTDIR`, `TESTDIR2`, `NEW_TESTDIR2`, `TESTDIR3`, `NEW_TESTDIR3`, `TESTFILE`, `NEW_TESTFILE`, `TESTFILE2`, `NEW_TESTFILE2`, `TESTFILE3`, `TESTFILE4`, `TESTFILE5`, `NEW_TESTFILE5`, `DIRMODE`, `FILEMODE`.

## Control Flow

Function-level flow is organized around `setup`, `cleanup`, `renameat_verify`, `main`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. This file uses the older `test.h` harness: `main` parses options, loops over configured cases or signals, calls direct syscall wrappers, reports through `tst_resm`/`tst_brkm`, and exits through `tst_exit`. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed. The test expects root privileges or temporarily changes credentials/capabilities.

## Dependencies and Integration Points

Direct includes: `<sys/types.h>`, `<sys/stat.h>`, `<sys/time.h>`, `<stdlib.h>`, `<errno.h>`, `<string.h>`, `<signal.h>`, `<sys/mount.h>`, `"test.h"`, `"tso_safe_macros.h"`, `"lapi/fcntl.h"`. Uses the older LTP `test.h` harness and legacy result macros. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

filesystem-specific behavior can require TCONF gating Explicit errno expectations include `EBADF`, `ENOTDIR`, `ELOOP`, `EROFS`, `EMLINK`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; TCONF for unsupported kernel, filesystem, or feature combinations; TBROK for fixture/setup failures; notable reported messages include `renameat01`; `Failed to obtain block device`; `renameat() succeeded unexpectedly`; `renameat() failed unexpectedly`; `renameat() returned the expected value`.
