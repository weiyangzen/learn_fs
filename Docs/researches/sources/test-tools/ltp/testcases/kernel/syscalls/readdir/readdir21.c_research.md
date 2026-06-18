# sources/test-tools/ltp/testcases/kernel/syscalls/readdir/readdir21.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/readdir/readdir21.c` is a 81-line LTP source file in the `readdir` syscall test area. legacy readdir syscall coverage for directory enumeration and descriptor/type errors across mounted filesystems. Source description: Author: Zeng Linggang <zenglg.jy@cn.fujitsu.com>

## Important APIs, Types, and Functions

called APIs/macros: `readdir`, `SAFE_MKDIR`, `SAFE_OPEN`, `SAFE_RMDIR`, `TST_EXP_FAIL`; local functions: `setup`, `verify_readdir`; struct/table types referenced: `struct old_linux_dirent`, `struct tcase`, `struct tst_test`; important macros/constants: `MNTPOINT`, `TEST_DIR`, `TEST_DIR4`, `TEST_FILE`, `DIR_MODE`.

## Control Flow

Function-level flow is organized around `setup`, `verify_readdir`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed. The test expects root privileges or temporarily changes credentials/capabilities. It integrates with LTP device mounting or filesystem-matrix execution.

## Dependencies and Integration Points

Direct includes: `<sys/stat.h>`, `"tst_test.h"`, `"lapi/syscalls.h"`, `"lapi/readdir.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.tcnt`, `.setup`, `.test`, `.needs_root`, `.all_filesystems`, `.mount_device`, `.mntpoint`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

bad-address cases are architecture and fault-path sensitive; filesystem-specific behavior can require TCONF gating Explicit errno expectations include `ENOENT`, `ENOTDIR`, `EBADFD`, `EFAULT`, `EBADF`.

## Test Signals

TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `lapi/readdir.h`; `readdir() with %s`.
