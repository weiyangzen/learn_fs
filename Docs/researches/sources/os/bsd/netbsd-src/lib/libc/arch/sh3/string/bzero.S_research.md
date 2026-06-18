# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/string/bzero.S

## Summary
Builds SH3 `bzero` from the common local `memset.S` source.

## Key Details
- Defines `BZERO`.
- Includes `memset.S`.

## Notes
The actual zeroing implementation is in `memset.S`.
