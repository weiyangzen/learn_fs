# sources/test-tools/ltp/testcases/kernel/syscalls/readdir/readdir01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/readdir/readdir01.c` is a 73-line LTP source file in the `readdir` syscall test area. legacy readdir syscall coverage for directory enumeration and descriptor/type errors across mounted filesystems. Source description: Contact information: Silicon Graphics, Inc., 1600 Amphitheatre Pkwy, Mountain View, CA  94043, or: http://www.sgi.com For further information regarding this notice, see: http://oss.sgi.com/projects/GenInfo/NoticeExplan/

## Important APIs, Types, and Functions

called APIs/macros: `readdir`, `SAFE_CLOSE`, `SAFE_CLOSEDIR`, `SAFE_OPEN`, `SAFE_OPENDIR`, `SAFE_READDIR`, `SAFE_WRITE`; local functions: `setup`, `verify_readdir`; struct/table types referenced: `struct dirent`, `struct tst_test`; important macros/constants: `MNTPOINT`.

## Control Flow

Function-level flow is organized around `setup`, `verify_readdir`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed. The test expects root privileges or temporarily changes credentials/capabilities. It integrates with LTP device mounting or filesystem-matrix execution.

## Dependencies and Integration Points

Direct includes: `<stdio.h>`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.setup`, `.test_all`, `.needs_root`, `.all_filesystems`, `.mount_device`, `.mntpoint`.

## Risks and Edge Cases

filesystem-specific behavior can require TCONF gating

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `readdirfile`.
