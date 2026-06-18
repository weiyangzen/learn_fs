# sources/test-tools/ltp/testcases/kernel/syscalls/read/read01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/read/read01.c` is a 45-line LTP source file in the `read` syscall test area. read syscall coverage for ordinary files, directories, invalid buffers, O_DIRECT, FIFOs, short/complete reads, and expected errno paths.

## Important APIs, Types, and Functions

called APIs/macros: `read`, `SAFE_CLOSE`, `SAFE_LSEEK`, `SAFE_OPEN`, `SAFE_WRITE`, `TEST`; local functions: `verify_read`, `setup`, `cleanup`; struct/table types referenced: `struct tst_test`; important macros/constants: `SIZE`.

## Control Flow

Function-level flow is organized around `verify_read`, `setup`, `cleanup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed.

## Dependencies and Integration Points

Direct includes: `<errno.h>`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.test_all`, `.setup`, `.cleanup`, `.needs_tmpdir`.

## Risks and Edge Cases

The main risk is errno drift or unsupported syscall behavior across architectures, kernel versions, and libc wrapper availability.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `read(2) failed`; `read(2) returned %ld`.
