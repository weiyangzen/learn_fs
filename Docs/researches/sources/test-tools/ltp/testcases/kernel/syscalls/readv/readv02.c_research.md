# sources/test-tools/ltp/testcases/kernel/syscalls/readv/readv02.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/readv/readv02.c` is a 103-line LTP source file in the `readv` syscall test area. readv vector-read coverage for normal reads and invalid iovec/count/descriptor cases. Source description: 07/2001 Ported by Wayne Boyer 05/2002 Ported by Jacky Malcles

## Important APIs, Types, and Functions

called APIs/macros: `readv`, `SAFE_CLOSE`, `SAFE_FILE_PRINTF`, `SAFE_MKDIR`, `SAFE_OPEN`, `TST_EXP_FAIL2`; local functions: `verify_readv`, `setup`, `cleanup`; struct/table types referenced: `struct iovec`, `struct tcase`, `struct tst_test`; important macros/constants: `K_1`, `MODES`, `CHUNK`.

## Control Flow

Function-level flow is organized around `verify_readv`, `setup`, `cleanup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed.

## Dependencies and Integration Points

Direct includes: `<sys/uio.h>`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.tcnt`, `.needs_tmpdir`, `.setup`, `.cleanup`, `.test`.

## Risks and Edge Cases

bad-address cases are architecture and fault-path sensitive Explicit errno expectations include `EINVAL`, `EFAULT`, `EISDIR`, `EBADF`.

## Test Signals

TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `readv(%d, %p, %d)`.
