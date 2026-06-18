# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/stdlib/abs.S

## Summary
Implements SPARC64 `abs()`.

## Key Details
- Computes the negated candidate in `%o1`.
- Uses conditional move `movrlz` to return the negated value only when the input is negative.
- Returns through `retl`.

## Notes
This is a compact v9a-style branch-minimized implementation.
