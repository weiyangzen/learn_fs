# sources/test-tools/strace/src/linux/x32/arch_sigreturn.c

## Purpose
Reuses x86_64 old-sigreturn handling for x32. The included x86_64 file states that only the x86 personality has the old `sigreturn` syscall and includes the i386 implementation.

## Important APIs, Types, and Functions
Includes `../x86_64/arch_sigreturn.c`, which in turn includes `../i386/arch_sigreturn.c` to provide `arch_sigreturn`.

## Control Flow and Integration
Generic `sigreturn.c` calls `arch_sigreturn` when decoding old signal return. In x32 builds, this path is relevant to the 32-bit personality rather than native x32 syscalls.

## State and Persistence
No persistent state. It reads tracee stack memory and emits decoded signal mask data through inherited logic.

## Dependencies
Depends on i386 signal frame layout and personality routing so old `sigreturn` is not applied to unsupported x32/native paths.

## Risks
Incorrect personality routing could try to decode an old i386 sigframe for a native x32 context. The include chain hides the actual implementation, so regressions in i386 signal code affect x32.

## Test Signals
Exercise old `sigreturn` from an i386 personality under x32 strace and confirm native x32 does not misreport unsupported old signal return behavior.
