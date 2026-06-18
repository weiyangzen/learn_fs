# sources/test-tools/strace/src/linux/x32/arch_get_personality.c

## Purpose
Reuses x86_64 syscall-info personality detection for x32.

## Important APIs, Types, and Functions
Includes `../x86_64/arch_get_personality.c`, which implements `get_personality_from_syscall_info`. In an x32 build with `X32` defined, the included code returns `1` for `AUDIT_ARCH_I386` and `0` otherwise, because the x86_64-only x32-bit discrimination block is disabled.

## Control Flow and Integration
Called by generic personality selection when `PTRACE_GET_SYSCALL_INFO` is available. For x32, audit arch `AUDIT_ARCH_X86_64` corresponds to personality 0 and `AUDIT_ARCH_I386` to personality 1.

## State and Persistence
No local state. The generic layer records the selected personality on the tracee control block.

## Dependencies
Depends on x86_64 implementation, `AUDIT_ARCH_I386`, and x32 build defines matching `arch_defs_.h` personality order.

## Risks
If the x32 build environment does not define `X32` as expected, the inherited x86_64 code could return personality 2 for x32-bit-marked syscalls, which is out of range for this two-personality target.

## Test Signals
Trace x32 and i386 processes with syscall-info enabled and verify personality indexes remain 0 and 1 only.
