# sources/test-tools/ltp/testcases/kernel/syscalls/read/read02.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/read/read02.c` is a 130-line LTP source file in the `read` syscall test area. read syscall coverage for ordinary files, directories, invalid buffers, O_DIRECT, FIFOs, short/complete reads, and expected errno paths. Source description: Ported to LTP: Wayne Boyer 04/2017 Modified by Jinhui Huang

## Important APIs, Types, and Functions

called APIs/macros: `read`, `SAFE_CLOSE`, `SAFE_FILE_PRINTF`, `SAFE_MEMALIGN`, `SAFE_MMAP`, `SAFE_OPEN`, `TEST`; local functions: `verify_read`, `setup`, `cleanup`; struct/table types referenced: `struct tcase`, `struct tst_test`; important macros/constants: `_GNU_SOURCE`.

## Control Flow

Function-level flow is organized around `verify_read`, `setup`, `cleanup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed.

## Dependencies and Integration Points

Direct includes: `<stdio.h>`, `<stdlib.h>`, `<errno.h>`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.tcnt`, `.test`, `.setup`, `.cleanup`, `.needs_tmpdir`.

## Risks and Edge Cases

bad-address cases are architecture and fault-path sensitive; filesystem-specific behavior can require TCONF gating Explicit errno expectations include `EBADF`, `EISDIR`, `EFAULT`, `EINVAL`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; TCONF for unsupported kernel, filesystem, or feature combinations; notable reported messages include `O_DIRECT not supported on %s filesystem`; `O_DIRECT unaligned reads fallbacks to buffered I/O`; `read() succeeded unexpectedly`; `read() failed as expected`; `read() failed unexpectedly, `.
