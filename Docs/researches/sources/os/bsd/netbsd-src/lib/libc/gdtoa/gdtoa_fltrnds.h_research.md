# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/gdtoa_fltrnds.h

Purpose: Inline include fragment for selecting an `FPI` adjusted to the current floating-point rounding mode.

Core behavior:
- Declares local `fpi`, `fpi1`, and `Rounding` variables for callers.
- Uses `Flt_Rounds` when `Trust_FLT_ROUNDS` is defined.
- Otherwise maps `fegetround()` to gdtoa rounding values.
- Reuses `fpi0` for round-to-nearest and copies it into `fpi1` for directed rounding.

Dependencies:
- Must be included inside functions that already define `fpi0`.
- Relies on `Flt_Rounds`, `fegetround`, and `FPI` definitions from `gdtoaimp.h`.
