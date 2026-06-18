# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfemu.c

## Role

`gsfemu.c` is a GCC-compatible software floating-point emulation layer for Ghostscript builds that lack hardware/libgcc floating point support.

This is numeric runtime support, not filesystem code.

## Main Interfaces

Implements GCC helper routines for:

- Double/single negation: `__negdf2`, `__negsf2`
- Double/single add/subtract: `__adddf3`, `__subdf3`, `__addsf3`, `__subsf3`
- Double/single multiplication and division: `__muldf3`, `__mulsf3`, `__divdf3`, `__divsf3`
- Double/single comparisons: `__eq*2`, `__ne*2`, `__gt*2`, `__ge*2`, `__lt*2`, `__le*2`
- Conversions: `__fixdfsi`, `__fixsfsi`, `__floatsidf`, `__floatsisf`, `__truncdfsf2`, `__extendsfdf2`

## Important Behavior

- Works by inspecting IEEE-754 single and double bit layouts directly.
- Supports big- and little-endian double word ordering through `msw`/`lsw`.
- Raises `SIGFPE` for selected overflow/divide-by-zero cases.
- Returns zero rather than denormalized values in several underflow paths.
- Uses round-to-nearest only.
- Includes an optional `TEST` program with randomized checks.

## Notable Risks

- The file explicitly says it is not a complete IEEE implementation: NaNs and denormals are incomplete.
- It relies on type-punning through pointer casts, which is fragile under modern strict-aliasing assumptions.
- Division comments state quotient rounding is not implemented.
- Overflow handling is partial and oriented toward old GCC helper expectations.
