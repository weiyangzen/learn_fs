# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/stdlib/Makefile.inc

## Summary
x86_64 stdlib build fragment.

## Key Details
- Adds assembly sources `abs.S`, `div.S`, `labs.S`, and `ldiv.S`.
- Marks `llabs.S`, `imaxabs.S`, and `imaxdiv.S` as not sourced.

## Notes
`labs.S` supplies weak aliases for `llabs` and `imaxabs`.
