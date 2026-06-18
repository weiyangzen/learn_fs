# sources/test-tools/ltp/testcases/kernel/syscalls/realpath/realpath01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/realpath/realpath01.c` is a 45-line LTP source file in the `realpath` syscall test area. realpath libc path canonicalization coverage for success and error paths over temporary filesystem fixtures. Source description: Based on the reproducer posted upstream so other copyrights may apply. Author: Dmitry V. Levin <ldv@altlinux.org> LTP conversion from glibc source: Petr Vorel <pvorel@suse.cz>

## Important APIs, Types, and Functions

called APIs/macros: `realpath`, `SAFE_CHROOT`, `SAFE_MKDIR`, `TST_EXP_FAIL_PTR_NULL`; local functions: `setup`, `run`; struct/table types referenced: `struct tst_test`, `struct tst_tag`; important macros/constants: `CHROOT_DIR`.

## Control Flow

Function-level flow is organized around `setup`, `run`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed. The test expects root privileges or temporarily changes credentials/capabilities.

## Dependencies and Integration Points

Direct includes: `"tst_test.h"`, `<errno.h>`, `<stdlib.h>`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.test_all`, `.setup`, `.needs_root`, `.needs_tmpdir`, `.tags`.

## Risks and Edge Cases

The main risk is errno drift or unsupported syscall behavior across architectures, kernel versions, and libc wrapper availability. Explicit errno expectations include `ENOENT`.

## Test Signals

TFAIL/TST_EXP_FAIL errno or invariant checks.
