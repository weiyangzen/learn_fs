# sources/test-tools/strace/src/linux/x32/get_error.c

## Purpose
Reuses x86_64 syscall return and errno decoding for x32.

## Important APIs, Types, and Functions
Includes `../x86_64/get_error.c`, which reads the x86 register cache, detects negated errno according to syscall-table flags, and populates `tcp->u_rval`/`tcp->u_error`.

## Control Flow and Integration
Generic syscall-exit handling calls the inherited `arch_get_error`. x32 returns values in the x86_64 `rax` register, so sharing x86_64 logic is expected.

## State and Persistence
Mutates only per-tracee syscall result fields. Reads transient x86 register cache state.

## Dependencies
Depends on included x86_64 register definitions and generic error handling.

## Risks
Return-value width is subtle for x32 because user longs are 32-bit while registers are 64-bit. The inherited code must preserve strace's kernel-long handling for x32.

## Test Signals
Trace x32 syscalls with success, negative errno, and large unsigned returns. Fault injection should verify printed errno and return values.
