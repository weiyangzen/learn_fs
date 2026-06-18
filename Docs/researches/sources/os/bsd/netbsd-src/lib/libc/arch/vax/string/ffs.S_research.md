# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/string/ffs.S

## Summary
Implements VAX `ffs()`.

## Key Details
- Uses the VAX `ffs` instruction over 32 bits.
- Converts the instruction's zero-based bit index to the C one-based result.
- Returns zero when no bit is set.

## Notes
The no-bit case is handled by setting `-1` then incrementing.
