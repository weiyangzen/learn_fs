# sources/test-tools/strace/src/linux/x32/check_scno.c

## Purpose
Rejects unsupported 64-bit syscall mode when running an x32 strace target.

## Important APIs, Types, and Functions
Defines `arch_check_scno(struct tcb *tcp)`. It reads `ptrace_sci.entry.nr`, and if current personality is x32 (`currpers == 0`) but the syscall number lacks `__X32_SYSCALL_BIT`, it prints an error and returns `0` to ignore the syscall.

## Control Flow and Integration
Generic `get_scno` calls this when syscall-info data is valid and `ARCH_NEEDS_NON_SHUFFLED_SCNO_CHECK` is set. Valid x32 or i386 syscalls return `1`; unsupported 64-bit syscalls return ignore.

## State and Persistence
No persistent state. It reads `tcp->currpers`, syscall-info global data, and emits an error message.

## Dependencies
Depends on `ptrace_sci`, `__X32_SYSCALL_BIT`, `PRI_klu`, and personality numbering from `arch_defs_.h`.

## Risks
This is a protective gate: without it, an x32-only build could try to decode regular x86_64 syscalls with the x32 table. False positives would hide valid syscalls; false negatives would produce wrong decoding.

## Test Signals
Tests should simulate or trace a syscall-info entry with `AUDIT_ARCH_X86_64` and no x32 bit in personality 0 and assert the unsupported-mode error and ignored return. Valid x32-bit-marked syscalls should pass.
