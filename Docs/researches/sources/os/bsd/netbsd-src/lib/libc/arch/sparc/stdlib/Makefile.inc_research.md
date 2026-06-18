# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/stdlib/Makefile.inc

## Summary
SPARC stdlib build fragment.

## Key Details
- Adds `llabs.S`.
- Marks `imaxabs.S` as not sourced.

## Notes
`llabs.S` also supplies `imaxabs` through weak aliasing.
