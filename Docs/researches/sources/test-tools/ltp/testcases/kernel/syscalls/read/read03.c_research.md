# sources/test-tools/ltp/testcases/kernel/syscalls/read/read03.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/read/read03.c` is a 54-line LTP source file in the `read` syscall test area. read syscall coverage for ordinary files, directories, invalid buffers, O_DIRECT, FIFOs, short/complete reads, and expected errno paths.

## Important APIs, Types, and Functions

called APIs/macros: `read`, `SAFE_CLOSE`, `SAFE_MKNOD`, `SAFE_OPEN`, `SAFE_STAT`, `SAFE_UNLINK`, `TST_EXP_FAIL`; local functions: `verify_read`, `setup`, `cleanup`; struct/table types referenced: `struct stat`, `struct tst_test`.

## Control Flow

Function-level flow is organized around `verify_read`, `setup`, `cleanup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed.

## Dependencies and Integration Points

Direct includes: `<stdio.h>`, `<fcntl.h>`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.needs_tmpdir`, `.setup`, `.cleanup`, `.test_all`.

## Risks and Edge Cases

The main risk is errno drift or unsupported syscall behavior across architectures, kernel versions, and libc wrapper availability. Explicit errno expectations include `EAGAIN`.

## Test Signals

TFAIL/TST_EXP_FAIL errno or invariant checks; TBROK for fixture/setup failures; notable reported messages include `read() when nothing is written to a pipe`.
