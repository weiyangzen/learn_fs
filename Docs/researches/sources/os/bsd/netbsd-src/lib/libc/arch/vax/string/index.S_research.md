# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/string/index.S

## Summary
Implements VAX `index()`.

## Key Details
- Searches for the first occurrence of a character in a NUL-terminated string.
- Special-cases search for `'\0'`.
- Returns pointer to match or zero if not found.

## Notes
This is the historical BSD name corresponding to `strchr`.
