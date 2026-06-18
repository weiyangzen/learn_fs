# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/string/bcmp.S

## Summary
Implements VAX `bcmp()`.

## Key Details
- Compares data in 32-bit word chunks first.
- Handles the remaining one to three bytes byte-by-byte.
- Returns zero for equality and nonzero for inequality.
- Avoids `cmpc3` because it is not portable across all VAX systems.

## Notes
The comment notes this manual approach is still faster than generic C on a MicroVAX II.
