# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/string/strncmp.S

## Summary
Implements x86_64 `strncmp()`.

## Key Details
- Returns zero immediately when count reaches zero.
- Compares bytes using an eight-times-unrolled loop.
- Stops on NUL or mismatch.
- Returns unsigned byte difference between the first differing characters.

## Notes
The unroll factor is explicitly chosen as a balance between speed and instruction-cache footprint.
