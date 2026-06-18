# sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename12.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename12.c` is a 67-line LTP source file in the `rename` syscall test area. rename filesystem semantics coverage for success, replacement, directory constraints, sticky permissions, hard links, and errno cases. Source description: 07/2001 Ported by Wayne Boyer

## Important APIs, Types, and Functions

called APIs/macros: `rename`, `SAFE_CHDIR`, `SAFE_CHMOD`, `SAFE_GETPWNAM`, `SAFE_MKDIR`, `SAFE_SETEUID`, `SAFE_STAT`, `SAFE_TOUCH`, `TEST`; local functions: `setup`, `run`; struct/table types referenced: `struct stat`, `struct passwd`, `struct tst_test`; important macros/constants: `MNT_POINT`, `TEMP_DIR`, `TEMP_FILE1`, `TEMP_FILE2`.

## Control Flow

Function-level flow is organized around `setup`, `run`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state.

## State and Persistence Behavior

State is temporary filesystem structure: files, directories, links, permissions, mount points, and expected post-rename path existence/content. Most cases mutate dentries and then validate the resulting tree. The test expects root privileges or temporarily changes credentials/capabilities. It integrates with LTP device mounting or filesystem-matrix execution.

## Dependencies and Integration Points

Direct includes: `<stdio.h>`, `<pwd.h>`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.setup`, `.test_all`, `.needs_root`, `.mntpoint`, `.mount_device`, `.all_filesystems`, `.skip_filesystems`.

## Risks and Edge Cases

permission cases depend on credentials, capabilities, and filesystem mode bits; filesystem-specific behavior can require TCONF gating Explicit errno expectations include `EPERM`, `EACCES`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `rename() failed as expected`; `rename() succeeded unexpectedly`; `rename() failed, but not with expected errno`.
