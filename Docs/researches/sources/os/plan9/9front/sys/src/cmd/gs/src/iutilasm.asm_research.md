# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iutilasm.asm

Contains legacy MS-DOS assembly support for the Ghostscript interpreter. Under `FOR80386`, it replaces Turbo C long multiply/divide/modulo library routines with 80386-prefixed 32-bit operations. Without `FOR80386`, it implements optimized 32-bit signed and unsigned division/modulo routines using 16-bit instructions, including Knuth-style normalization for 32-by-32 division.

Under `NOFPU`, it implements fixed-point multiply helpers `_fmul2fixed_` and `_dfmul2fixed_`, intended to avoid slow emulated floating point on systems without an FPU. The file also implements `_memflip8x8`, an 8-by-8 bit matrix transpose used by bitmap code.

This file is platform-specific compatibility/performance code and is unrelated to Plan 9 runtime behavior except as vendored Ghostscript source.
