# File Research: sources/os/bsd/netbsd-src/lib/libc_fp/arch/mips/Makefile.inc

## Purpose
Configures MIPS `libc_fp` to build hard-float implementations of soft-float ABI helper routines.

## Build Behavior
Adds `-mhard-float`, disables `MKSOFTFLOAT`, and selects `fpsf.S` and `fpdf.S` with hard-float assembler flags.

## Dependencies
Depends on MIPS assembler/compiler support for hard-float instructions.

## Risks And Notes
These objects are intended to be ABI-compatible with soft-float callers while executing on hardware with floating-point support.
