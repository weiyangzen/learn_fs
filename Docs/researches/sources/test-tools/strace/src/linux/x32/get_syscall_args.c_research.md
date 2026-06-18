# sources/test-tools/strace/src/linux/x32/get_syscall_args.c

## Purpose
Reuses x86_64 syscall argument extraction for x32.

## Important APIs, Types, and Functions
Includes `../x86_64/get_syscall_args.c`, which copies arguments from x86 syscall argument registers into `tcp->u_arg[]`, with i386 handling for compat personalities.

## Control Flow and Integration
Called by generic `get_syscall_args` after syscall number/personality resolution. x32 native syscalls use x86_64 register calling convention with ILP32 argument interpretation.

## State and Persistence
Mutates `tcp->u_arg[]` for the current syscall only.

## Dependencies
Depends on x86_64 register cache, personality-aware argument extraction, and x32 word-size handling in downstream decoders.

## Risks
Argument register order must be x86_64 order for x32 native and i386 order for personality 1. Width-sensitive decoders must interpret `u_arg` using the current personality, not host C long size.

## Test Signals
Trace x32 syscalls with six arguments, pointer arguments, and 64-bit offset pairs. Compare against i386 personality traces to verify switching.
