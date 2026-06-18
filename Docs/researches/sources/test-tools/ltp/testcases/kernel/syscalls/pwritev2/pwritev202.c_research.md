# sources/test-tools/ltp/testcases/kernel/syscalls/pwritev2/pwritev202.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/pwritev2/pwritev202.c` is a 118-line LTP source file in the `pwritev2` syscall test area. pwritev2 vector-positioned write coverage, including offset handling, iovec validation, flags, bad descriptors, and pipe errors. Source description: Author: Jinhui Huang <huangjh.jy@cn.fujitsu.com>

## Important APIs, Types, and Functions

called APIs/macros: `pwritev2`, `SAFE_CLOSE`, `SAFE_FTRUNCATE`, `SAFE_OPEN`, `SAFE_PIPE`, `TEST`; local functions: `verify_pwritev2`, `setup`, `cleanup`; struct/table types referenced: `struct iovec`, `struct tcase`, `struct tst_test`; important macros/constants: `_GNU_SOURCE`, `CHUNK`.

## Control Flow

Function-level flow is organized around `verify_pwritev2`, `setup`, `cleanup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed.

## Dependencies and Integration Points

Direct includes: `<sys/uio.h>`, `<unistd.h>`, `"tst_test.h"`, `"lapi/uio.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.tcnt`, `.setup`, `.cleanup`, `.test`, `.needs_tmpdir`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

bad-address cases are architecture and fault-path sensitive Explicit errno expectations include `EINVAL`, `EOPNOTSUPP`, `EFAULT`, `EBADF`, `ESPIPE`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `pwritev2() succeeded unexpectedly`; `pwritev2() failed as expected`; `pwritev2() failed unexpectedly, expected %s`.
