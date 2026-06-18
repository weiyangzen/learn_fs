# sources/test-tools/ltp/testcases/kernel/syscalls/sbrk/sbrk02.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/sbrk/sbrk02.c` is a 37-line LTP source file in the `sbrk` syscall test area. sbrk/brk coverage for heap growth/shrink success, ENOMEM failure, and 32-bit overflow regression behavior. Source description: Author: Zeng Linggang <zenglg.jy@cn.fujitsu.com>

## Important APIs, Types, and Functions

called APIs/macros: `sbrk`, `TST_EXP_FAIL_PTR_VOID`; local functions: `run`, `setup`; struct/table types referenced: `struct tst_test`; important macros/constants: `INC`.

## Control Flow

Function-level flow is organized around `run`, `setup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state.

## State and Persistence Behavior

State is the process program break and virtual address space. The tests do not persist data beyond the process lifetime.

## Dependencies and Integration Points

Direct includes: `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.test_all`, `.setup`.

## Risks and Edge Cases

The main risk is errno drift or unsupported syscall behavior across architectures, kernel versions, and libc wrapper availability. Explicit errno expectations include `ENOMEM`.

## Test Signals

TFAIL/TST_EXP_FAIL errno or invariant checks.
