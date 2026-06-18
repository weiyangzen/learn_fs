# sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename09.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename09.c` is a 61-line LTP source file in the `rename` syscall test area. rename filesystem semantics coverage for success, replacement, directory constraints, sticky permissions, hard links, and errno cases. Source description: 07/2001 Ported by Wayne Boyer

## Important APIs, Types, and Functions

called APIs/macros: `rename`, `SAFE_CHOWN`, `SAFE_MKDIR`, `SAFE_SETEUID`, `SAFE_TOUCH`, `TST_EXP_FAIL`; local functions: `setup`, `run`; struct/table types referenced: `struct tst_test`; important macros/constants: `SRCDIR`, `DESTDIR`, `SRCFILE`, `DESTFILE`, `PERMS`.

## Control Flow

Function-level flow is organized around `setup`, `run`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state.

## State and Persistence Behavior

State is temporary filesystem structure: files, directories, links, permissions, mount points, and expected post-rename path existence/content. Most cases mutate dentries and then validate the resulting tree. The test expects root privileges or temporarily changes credentials/capabilities.

## Dependencies and Integration Points

Direct includes: `<stdio.h>`, `<stdlib.h>`, `<sys/types.h>`, `"tst_test.h"`, `"tst_safe_file_ops.h"`, `"tst_uid.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.test_all`, `.setup`, `.needs_root`, `.needs_tmpdir`.

## Risks and Edge Cases

permission cases depend on credentials, capabilities, and filesystem mode bits Explicit errno expectations include `EACCES`.

## Test Signals

TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `rename()`.
