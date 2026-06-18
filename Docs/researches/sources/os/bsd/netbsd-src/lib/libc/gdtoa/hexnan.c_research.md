# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/hexnan.c

Purpose: Parses hexadecimal NaN payloads such as `NaN(...)`.

Core behavior:
- Allows optional whitespace and optional `0x` prefixes inside the payload.
- Accumulates hex digits into the target significand word array.
- Supports multiple whitespace-separated hex fields.
- Truncates payload bits to the target `FPI` precision.
- Ensures a nonzero payload for `STRTOG_NaNbits`.
- Falls back to plain `STRTOG_NaN` for invalid or absent payloads.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `hexdig`, `hexdig_init_D2A`, and internal `L_shift`.
