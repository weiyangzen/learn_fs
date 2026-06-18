# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/string/memcmp.S

## Summary
Implements VAX `memcmp()`.

## Key Details
- Compares 32-bit words first.
- Backs up and compares bytes when a word differs.
- Handles trailing bytes after word comparison.
- Returns the unsigned byte difference for the first differing byte, or zero for equality.

## Notes
The fallback from word mismatch preserves standard `memcmp` byte-order semantics.
