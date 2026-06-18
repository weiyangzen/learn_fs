# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/stdlib/Makefile.inc

## Summary
VAX stdlib build fragment.

## Key Details
- Adds `erand48.c`.
- Marks `erand48_ieee754.c` as not sourced.

## Notes
VAX requires a non-IEEE754 random floating conversion path.
