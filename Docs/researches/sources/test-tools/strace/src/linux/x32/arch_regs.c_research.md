# sources/test-tools/strace/src/linux/x32/arch_regs.c

## Purpose
Reuses x86_64 register-cache setup for x32 syscall tracing.

## Important APIs, Types, and Functions
Includes `../x86_64/arch_regs.c`, which defines a union of `struct user_regs_struct` and an i386 register struct, an `iovec` for `PTRACE_GETREGSET`, `ARCH_REGS_FOR_GETREGSET`, `ARCH_IOVEC_FOR_GETREGSET`, and PC/SP macros that switch on returned iovec length.

## Control Flow and Integration
Generic register helpers fetch registers into the shared union. PC and SP references evaluate to i386 or x86_64 fields depending on the fetched size. The included code disables `ARCH_MIGHT_USE_SET_REGS`.

## State and Persistence
Uses static `x86_regs_union` and `x86_io` caches inside the strace process. They are transient and refreshed per tracee stop.

## Dependencies
Depends on x86_64 ptrace register structures, generic `GETREGSET` support, and x32 syscall helpers that read x86_64 register names.

## Risks
The shared union must be large enough for both layouts, and `iov_len` must accurately reflect current personality. Stale or mismatched `iov_len` causes wrong PC/SP selection.

## Test Signals
Trace x32 and i386 processes and verify PC/SP reporting, syscall arguments, and return values across personality switches.
