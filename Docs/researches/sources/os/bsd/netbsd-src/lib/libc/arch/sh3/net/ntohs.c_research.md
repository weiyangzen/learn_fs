# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/net/ntohs.c

## Summary
Implements the SH3 little-endian `ntohs()` conversion.

## Key Details
- Compiled only for little-endian targets.
- Uses one `swap.b` instruction to reverse the two bytes of a 16-bit value.
- Returns a `u_int16_t`.

## Notes
The function is absent for big-endian builds because network byte order already matches host order.
