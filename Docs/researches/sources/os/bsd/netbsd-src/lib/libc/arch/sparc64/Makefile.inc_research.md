# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/Makefile.inc

## Summary
Top-level SPARC64 libc architecture build fragment.

## Key Details
- Adds `__sigtramp2.S`.
- Adds assembler flag `-Wa,-Av9a` for files using v9a extensions.
- Adds `softfloat` to `.PATH` and builds `qp.c`.
- Defines `SOFTFLOATSPARC64_FOR_GCC`, `EXCEPTIONS_WITH_SOFTFLOAT`, and `SOFTFLOAT_NEED_FIXUNS`.
- Includes shared SoftFloat build rules unless `MKSOFTFLOAT == no`.
- When not using shared rules, builds `softfloat-wrapper.c` and adds include paths for softfloat sources.

## Notes
This fragment wires SPARC64 quad-precision support into libc.
