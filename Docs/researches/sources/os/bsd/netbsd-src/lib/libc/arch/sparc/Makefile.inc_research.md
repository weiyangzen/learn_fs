# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/Makefile.inc

## Summary
Top-level SPARC libc architecture build fragment.

## Key Details
- Adds `__sigtramp2.S`.
- Adds an include path for generated `assym.h`.
- For non-sparc64 SPARC builds, generates division and remainder assembly files from `gen/divrem.m4`.
- Generated files are `rem.S`, `sdiv.S`, `udiv.S`, and `urem.S`.
- Cleans generated outputs.

## Notes
The generated signed division object is named `sdiv.o` to avoid colliding with the ANSI C `div` function.
