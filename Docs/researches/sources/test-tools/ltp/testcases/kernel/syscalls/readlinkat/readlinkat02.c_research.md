# sources/test-tools/ltp/testcases/kernel/syscalls/readlinkat/readlinkat02.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/readlinkat/readlinkat02.c` is a 83-line LTP source file in the `readlinkat` syscall test area. readlinkat coverage for dirfd-relative symlink reads and invalid path, descriptor, and buffer cases. Source description: Author: Zeng Linggang <zenglg.jy@cn.fujitsu.com>

## Important APIs, Types, and Functions

called APIs/macros: `readlinkat`, `SAFE_CLOSE`, `SAFE_OPEN`, `SAFE_SYMLINK`, `TST_EXP_FAIL`; local functions: `verify_readlinkat`, `setup`, `cleanup`; struct/table types referenced: `struct tcase`, `struct tst_test`; important macros/constants: `TEST_FILE`, `SYMLINK_FILE`, `BUFF_SIZE`.

## Control Flow

Function-level flow is organized around `verify_readlinkat`, `setup`, `cleanup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed.

## Dependencies and Integration Points

Direct includes: `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.test`, `.needs_tmpdir`, `.setup`, `.cleanup`, `.tcnt`.

## Risks and Edge Cases

The main risk is errno drift or unsupported syscall behavior across architectures, kernel versions, and libc wrapper availability. Explicit errno expectations include `EINVAL`, `ENOTDIR`, `EBADF`, `ENOENT`.

## Test Signals

TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `readlinkat(%d, %s, NULL, %ld)`.
