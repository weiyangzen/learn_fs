# sources/test-tools/ltp/testcases/kernel/syscalls/rmdir/rmdir01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rmdir/rmdir01.c` is a 40-line LTP source file in the `rmdir` syscall test area. rmdir filesystem coverage for successful directory removal and error paths such as non-empty directories, loops, permissions, and read-only mounts.

## Important APIs, Types, and Functions

called APIs/macros: `rmdir`, `SAFE_MKDIR`, `TEST`; local functions: `verify_rmdir`; struct/table types referenced: `struct stat`, `struct tst_test`; important macros/constants: `TESTDIR`.

## Control Flow

Function-level flow is organized around `verify_rmdir`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed.

## Dependencies and Integration Points

Direct includes: `<errno.h>`, `<sys/stat.h>`, `<sys/types.h>`, `<unistd.h>`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.test_all`, `.needs_tmpdir`.

## Risks and Edge Cases

The main risk is errno drift or unsupported syscall behavior across architectures, kernel versions, and libc wrapper availability.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `rmdir(%s) failed`.
