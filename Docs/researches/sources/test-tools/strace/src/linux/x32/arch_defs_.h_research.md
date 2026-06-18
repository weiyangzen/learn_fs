# sources/test-tools/strace/src/linux/x32/arch_defs_.h

## Purpose
Defines x32 build personality and ABI feature metadata. This strace target supports x32 as personality 0 and i386 as personality 1, not the full x86_64 three-personality arrangement.

## Important APIs, Types, and Functions
Sets `ARCH_NEEDS_NON_SHUFFLED_SCNO_CHECK 1`, structure and legacy syscall feature macros, `SUPPORTED_PERSONALITIES 2`, designators `{ "x32", "32" }`, names `{ "x32", "32 bit" }`, `PERSONALITY0_AUDIT_ARCH { AUDIT_ARCH_X86_64, __X32_SYSCALL_BIT }`, and `PERSONALITY1_AUDIT_ARCH { AUDIT_ARCH_I386, 0 }`.

## Control Flow and Integration
Compile-time definitions feed syscall table creation, filtering, seccomp audit-arch handling, and syscall-number shuffle/check logic. The non-shuffled syscall check is important because x32 syscall numbers carry `__X32_SYSCALL_BIT`.

## State and Persistence
No runtime state. Defines static build personality behavior.

## Dependencies
Depends on audit arch constants, `__X32_SYSCALL_BIT`, and generic defaults in `arch_defs.h`.

## Risks
Feature macros affect old stat, mmap, select, uid16, and time64 syscall availability. Incorrect personality audit masks can break seccomp filtering or classify x86_64 syscalls as x32.

## Test Signals
Build x32 strace and verify `-e trace=...@x32` and `@32` filters, seccomp filter generation, and syscall name lookup for x32-bit-marked syscall numbers.
