# sources/test-tools/ltp/testcases/kernel/syscalls/removexattr/removexattr02.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/removexattr/removexattr02.c` is a 128-line LTP source file in the `removexattr` syscall test area. removexattr extended-attribute coverage for successful removals and missing/invalid xattr or pathname errors. Source description: Author: Xiao Yang <yangx.jy@cn.fujitsu.com>

## Important APIs, Types, and Functions

called APIs/macros: `removexattr`, `SAFE_TOUCH`, `TEST`; local functions: `verify_removexattr`, `setup`, `cleanup`, `main`; struct/table types referenced: `struct test_case`.

## Control Flow

Function-level flow is organized around `verify_removexattr`, `setup`, `cleanup`, `main`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. This file uses the older `test.h` harness: `main` parses options, loops over configured cases or signals, calls direct syscall wrappers, reports through `tst_resm`/`tst_brkm`, and exits through `tst_exit`. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed.

## Dependencies and Integration Points

Direct includes: `"config.h"`, `<errno.h>`, `<sys/types.h>`, `<sys/xattr.h>`, `"test.h"`, `"tso_safe_macros.h"`. Uses the older LTP `test.h` harness and legacy result macros. Compile-time feature guards gate optional kernel/libc interfaces.

## Risks and Edge Cases

bad-address cases are architecture and fault-path sensitive Explicit errno expectations include `ENODATA`, `ENOENT`, `EFAULT`, `ENOTSUP`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; TCONF for unsupported kernel, filesystem, or feature combinations; notable reported messages include `No xattr support in fs or `; `removexattr() succeeded unexpectedly`; `removexattr() failed unexpectedly,`; ` expected %s`; `removexattr() failed as expected`.
