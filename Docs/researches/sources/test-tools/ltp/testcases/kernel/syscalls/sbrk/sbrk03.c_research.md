# sources/test-tools/ltp/testcases/kernel/syscalls/sbrk/sbrk03.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/sbrk/sbrk03.c` is a 70-line LTP source file in the `sbrk` syscall test area. sbrk/brk coverage for heap growth/shrink success, ENOMEM failure, and 32-bit overflow regression behavior.

## Important APIs, Types, and Functions

called APIs/macros: `sbrk`, `brk`; local functions: `sbrk_test`; struct/table types referenced: `struct tst_test`, `struct tst_tag`.

## Control Flow

Function-level flow is organized around `sbrk_test`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state.

## State and Persistence Behavior

State is the process program break and virtual address space. The tests do not persist data beyond the process lifetime.

## Dependencies and Integration Points

Direct includes: `<stdio.h>`, `<unistd.h>`, `"lapi/abisize.h"`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.test_all`, `.supported_archs`, `.needs_abi_bits`, `.tags`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

The main risk is errno drift or unsupported syscall behavior across architectures, kernel versions, and libc wrapper availability. Explicit errno expectations include `ENOMEM`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks.
