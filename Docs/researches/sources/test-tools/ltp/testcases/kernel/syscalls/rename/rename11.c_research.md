# sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename11.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename11.c` is a 187-line LTP source file in the `rename` syscall test area. rename filesystem semantics coverage for success, replacement, directory constraints, sticky permissions, hard links, and errno cases. Source description: Author: Xiaoguang Wang <wangxg.fnst@cn.fujitsu.com>

## Important APIs, Types, and Functions

called APIs/macros: `rename`, `SAFE_MKDIR`, `SAFE_MOUNT`, `SAFE_RMDIR`, `SAFE_SYMLINK`, `SAFE_TOUCH`, `SAFE_UNLINK`, `TEST`; local functions: `cleanup`, `setup`, `test_eloop`, `test_erofs`, `test_emlink`, `main`, `check_and_print`; important macros/constants: `MNTPOINT`, `TEST_EROFS`, `TEST_NEW_EROFS`, `TEST_EMLINK`, `TEST_NEW_EMLINK`, `TEST_NEW_ELOOP`, `ELOPFILE`.

## Control Flow

Function-level flow is organized around `cleanup`, `setup`, `test_eloop`, `test_erofs`, `test_emlink`, `main`, `check_and_print`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. This file uses the older `test.h` harness: `main` parses options, loops over configured cases or signals, calls direct syscall wrappers, reports through `tst_resm`/`tst_brkm`, and exits through `tst_exit`. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is temporary filesystem structure: files, directories, links, permissions, mount points, and expected post-rename path existence/content. Most cases mutate dentries and then validate the resulting tree. The test expects root privileges or temporarily changes credentials/capabilities.

## Dependencies and Integration Points

Direct includes: `<stdio.h>`, `<errno.h>`, `<sys/types.h>`, `<sys/stat.h>`, `<fcntl.h>`, `<sys/mount.h>`, `"test.h"`, `"tso_safe_macros.h"`. Uses the older LTP `test.h` harness and legacy result macros.

## Risks and Edge Cases

The main risk is errno drift or unsupported syscall behavior across architectures, kernel versions, and libc wrapper availability. Explicit errno expectations include `ELOOP`, `EROFS`, `EMLINK`, `ELOPFILE`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; TCONF for unsupported kernel, filesystem, or feature combinations; notable reported messages include `rename11`; `Failed to obtain block device`; `failed as expected`; `failed unexpectedly; expected - %d : %s`; `rename succeeded unexpectedly`.
