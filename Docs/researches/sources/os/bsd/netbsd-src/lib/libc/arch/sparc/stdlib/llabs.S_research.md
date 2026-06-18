# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/stdlib/llabs.S

## Summary
Implements SPARC `llabs()` and aliases `imaxabs()`.

## Key Details
- Tests the high 32-bit word of the 64-bit argument.
- If negative, subtracts low and high halves from zero using carry propagation.
- Returns the absolute value in `%o0:%o1`.
- Provides weak aliases for `llabs` and `imaxabs` when supported.

## Notes
The implementation handles a 64-bit integer split across SPARC 32-bit argument registers.
