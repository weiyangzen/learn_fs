# sources/test-tools/ltp/testcases/kernel/syscalls/readlinkat/readlinkat01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/readlinkat/readlinkat01.c` is a 98-line LTP source file in the `readlinkat` syscall test area. readlinkat coverage for dirfd-relative symlink reads and invalid path, descriptor, and buffer cases. Source description: Author: Yi Yang <yyangcdl@cn.ibm.com>

## Important APIs, Types, and Functions

called APIs/macros: `readlinkat`, `SAFE_CLOSE`, `SAFE_OPEN`, `SAFE_SYMLINK`, `TST_EXP_POSITIVE`; local functions: `verify_readlinkat`, `setup`, `cleanup`; struct/table types referenced: `struct tcase`, `struct tst_test`, `struct tst_buffers`; important macros/constants: `TEST_FILE`, `TEST_SYMLINK`.

## Control Flow

Function-level flow is organized around `verify_readlinkat`, `setup`, `cleanup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed.

## Dependencies and Integration Points

Direct includes: `<stdlib.h>`, `<stdio.h>`, `"tst_test.h"`, `"lapi/fcntl.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.test`, `.needs_tmpdir`, `.setup`, `.cleanup`, `.bufs`, `.tcnt`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

filesystem-specific behavior can require TCONF gating

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `readlink_file`; `readlink_symlink`; `readlinkat(%d, %s, %s, %ld)`.
