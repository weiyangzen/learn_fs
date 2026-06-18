# sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename15.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename15.c` is a 129-line LTP source file in the `rename` syscall test area. rename filesystem semantics coverage for success, replacement, directory constraints, sticky permissions, hard links, and errno cases. Source description: Authors: David Fenner, Jon Hendrickson

## Important APIs, Types, and Functions

called APIs/macros: `rename`, `SAFE_CLOSE`, `SAFE_CREAT`, `SAFE_RENAME`, `SAFE_STAT`, `SAFE_SYMLINK`, `SAFE_UNLINK`, `TST_EXP_EQ_LI`, `TST_EXP_FAIL`, `TST_EXP_PASS`; local functions: `test_existing`, `test_non_existing`, `test_creat`, `run`, `setup`; struct/table types referenced: `struct stat`, `struct tst_test`; important macros/constants: `MNTPOINT`, `OLDNAME`, `NEWNAME`, `OBJNAME`.

## Control Flow

Function-level flow is organized around `test_existing`, `test_non_existing`, `test_creat`, `run`, `setup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state.

## State and Persistence Behavior

State is temporary filesystem structure: files, directories, links, permissions, mount points, and expected post-rename path existence/content. Most cases mutate dentries and then validate the resulting tree. The test expects root privileges or temporarily changes credentials/capabilities. It integrates with LTP device mounting or filesystem-matrix execution.

## Dependencies and Integration Points

Direct includes: `"tst_test.h"`, `"tst_tmpdir.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.setup`, `.test_all`, `.all_filesystems`, `.mntpoint`, `.format_device`, `.needs_root`.

## Risks and Edge Cases

filesystem-specific behavior can require TCONF gating Explicit errno expectations include `ENOENT`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `Test rename() on symlink pointing to an existent path`; `Test rename() on symlink pointing to a non-existent path`; `Test rename() on symlink pointing to a path created lately`.
