# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/gdtoa/gd_qnan.h

## Summary
Defines x86_64 gdtoa quiet NaN bit patterns.

## Key Details
- Defines single and double precision quiet NaN words.
- Defines x87 long-double quiet NaN words.
- Defines `ldus_*` words for unpacked/significand ordering.
- Notes that AMD64 ABI long double has six bytes of tail padding.

## Notes
The constants reflect little-endian IEEE and x87 extended layouts.
