# sources/test-tools/strace/src/linux/x32/get_scno.c

## Purpose
Reuses x86_64 syscall-number extraction for x32.

## Important APIs, Types, and Functions
Includes `../x86_64/get_scno.c`, which reads `orig_rax`/syscall-info data, uses `__X32_SYSCALL_BIT` to distinguish x32 where applicable, updates personality, and assigns `tcp->scno`.

## Control Flow and Integration
The inherited logic runs inside generic `get_scno`. For x32 builds it must coordinate with `check_scno.c` and syscall-number shuffling so table indexes use the untagged number while validation sees the original x32 bit.

## State and Persistence
Mutates `tcp->scno` and current personality. Reads transient register/syscall-info state.

## Dependencies
Depends on x86_64 register cache, `__X32_SYSCALL_BIT`, and x32 two-personality definitions.

## Risks
The main risk is mishandling the x32 syscall bit, either stripping it too early for validation or leaving it in when indexing the syscall table. That would cause unsupported-mode errors or out-of-range table lookups.

## Test Signals
Trace x32 syscalls and confirm displayed syscall numbers/names match untagged x32 table entries. Also test i386 personality switching.
