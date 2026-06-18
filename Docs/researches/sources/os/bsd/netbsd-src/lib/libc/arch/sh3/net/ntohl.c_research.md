# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/net/ntohl.c

## Summary
Implements the SH3 little-endian `ntohl()` conversion.

## Key Details
- Compiled only when `BYTE_ORDER == LITTLE_ENDIAN`.
- Uses SH `swap.b`, `swap.w`, `swap.b` inline assembly to reverse a 32-bit word.
- Returns a `u_int32_t` network-to-host conversion result.

## Notes
Big-endian SH3 builds do not define a function here, relying on generic/no-op handling elsewhere.
