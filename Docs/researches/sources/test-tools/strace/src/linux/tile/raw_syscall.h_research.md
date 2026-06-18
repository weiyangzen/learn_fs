# sources/test-tools/strace/src/linux/tile/raw_syscall.h

## Purpose
Implements a Tile inline raw syscall helper for strace's own internal zero-argument syscalls.

## Important APIs, Types, and Functions
Defines guarded `raw_syscall_0(kernel_ulong_t nr, kernel_ulong_t *err)`. Inline assembly executes `swint1`, passes the syscall number in register `r10`, captures `r0` as return value and `r1` as error channel, marks clobbered registers, stores `*err = e`, and returns `r`.

## Control Flow and Integration
Used when architecture-specific raw syscall support is needed by strace internals. The function has no branches; the kernel trap transfers control and returns register results.

## State and Persistence
No persistent state. It writes through the caller-provided `err` pointer and clobbers CPU registers according to the assembly constraint list.

## Dependencies
Depends on Tile compiler register constraints such as `R00`, `R01`, and `R10`, `kernel_types.h`, and the Tile syscall ABI.

## Risks
Inline assembly is fragile: wrong clobbers can corrupt caller state, wrong constraints can fail compilation, and wrong syscall trap instruction breaks all internal raw syscalls. The helper reports the Tile convention's `r1` error channel, unlike `get_error.c` which reads tracee `r0` for historical ptrace reasons.

## Test Signals
Native Tile builds must compile the constraints. Runtime smoke tests should cover strace internal raw syscalls and compare returned value/error behavior against libc or kernel expectations.
