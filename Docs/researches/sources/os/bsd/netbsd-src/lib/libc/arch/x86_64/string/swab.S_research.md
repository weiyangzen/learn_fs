# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/string/swab.S

## Summary
Implements x86_64 `swab()`.

## Key Details
- Swaps source and destination registers to use string instructions.
- Clears direction flag.
- Converts byte count to word count.
- Handles an initial group of one to seven words.
- Copies the rest eight words at a time, swapping the two bytes of each word.

## Notes
Odd trailing bytes are ignored because `swab` operates on byte pairs.
