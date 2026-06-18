# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/stdlib/div.S

## Summary
Implements x86_64 `div()` for signed int division.

## Key Details
- Places numerator in `%eax`.
- Uses `cltd` and `idivl %esi`.
- Packs quotient and remainder into `%rax` by shifting `%rdx` and ORing.
- Returns the ABI `div_t` aggregate in registers.

## Notes
This source is public domain.
