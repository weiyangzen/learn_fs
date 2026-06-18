# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/stdlib/ldiv.S

## Summary
Implements x86_64 `ldiv()`.

## Key Details
- Provides weak alias from `ldiv` to `_ldiv` when supported.
- Uses `cqto` and `idivq`.
- Returns quotient and remainder according to the x86_64 aggregate return ABI.

## Notes
The file notes the code was copied from GCC 3.0 output.
