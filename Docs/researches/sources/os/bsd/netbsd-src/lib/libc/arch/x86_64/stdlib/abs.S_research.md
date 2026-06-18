# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/stdlib/abs.S

## Summary
Implements x86_64 `abs()`.

## Key Details
- Moves 32-bit input from `%edi` to `%eax`.
- Tests sign and negates if negative.
- Returns the absolute value in `%eax`.

## Notes
The `INT_MIN` overflow behavior follows normal two's-complement C library semantics.
