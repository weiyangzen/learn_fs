# sources/test-tools/ltp/testcases/kernel/syscalls/renameat2/renameat201.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/renameat2/renameat201.c` is a 163-line LTP source file in the `renameat2` syscall test area. renameat2 flag-specific rename coverage for RENAME_NOREPLACE and RENAME_EXCHANGE plus filesystem support differences.

## Important APIs, Types, and Functions

called APIs/macros: `renameat2`, `SAFE_MKDIR`, `SAFE_OPEN`, `SAFE_TOUCH`, `TEST`; local functions: `setup`, `cleanup`, `renameat2_verify`, `main`; struct/table types referenced: `struct test_case`; important macros/constants: `_GNU_SOURCE`, `TEST_DIR`, `TEST_DIR2`, `TEST_FILE`, `TEST_FILE2`, `TEST_FILE3`, `NON_EXIST`.

## Control Flow

Function-level flow is organized around `setup`, `cleanup`, `renameat2_verify`, `main`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. This file uses the older `test.h` harness: `main` parses options, loops over configured cases or signals, calls direct syscall wrappers, reports through `tst_resm`/`tst_brkm`, and exits through `tst_exit`. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed.

## Dependencies and Integration Points

Direct includes: `"test.h"`, `"tso_safe_macros.h"`, `"lapi/fcntl.h"`, `"renameat2.h"`. Uses the older LTP `test.h` harness and legacy result macros. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

renameat2 tests depend on syscall and filesystem flag support; filesystems that do not implement exchange/noreplace semantics must be detected cleanly. Explicit errno expectations include `EEXIST`, `ENOENT`, `EINVAL`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; TCONF for unsupported kernel, filesystem, or feature combinations; notable reported messages include `renameat2.h`; `renameat201`; `close olddirfd failed`; `close newdirfd failed`; `RENAME_EXCHANGE flag is not implemeted on %s`.
