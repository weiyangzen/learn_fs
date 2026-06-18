# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/string/bcopy.S

## Summary
Builds SH3 `bcopy` from the common local `memcpy.S` source.

## Key Details
- Defines `BCOPY`.
- Includes `memcpy.S`.

## Notes
Behavior is controlled by preprocessor paths inside `memcpy.S`; this file is only a selector wrapper.
