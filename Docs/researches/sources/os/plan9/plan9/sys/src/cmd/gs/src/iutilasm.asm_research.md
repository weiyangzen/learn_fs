# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iutilasm.asm

Purpose: provides MS-DOS x86 assembly support routines for Ghostscript interpreter builds.

Contents:
- Optional 80386 replacements for Turbo C long multiply/divide/modulo routines using 32-bit operand prefixes.
- Non-386 long signed/unsigned divide and modulo routines replacing slow Turbo C library implementations.
- Optional `NOFPU` fixed-point multiply routines (`_fmul2fixed_`, `_dfmul2fixed_`) for faster coordinate transformations without an FPU.
- `_memflip8x8`, an 8-by-8 bit-matrix transpose helper used for bitmap manipulation.

The assembly is heavily conditional on build flags such as `FOR80386`, `DEBUG`, and `NOFPU`. It is platform-specific legacy performance support, not portable interpreter logic.
