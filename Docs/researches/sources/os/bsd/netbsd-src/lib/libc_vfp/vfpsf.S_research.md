# File Research: sources/os/bsd/netbsd-src/lib/libc_vfp/vfpsf.S

## Purpose
Implements single-precision soft-float ABI helpers using ARM VFP instructions.

## Main Entry Points
Provides single add/subtract/multiply/divide/negate, double-to-single truncation, single-to-signed/unsigned int, int-to-single, unsigned-int-to-single, EABI reverse subtraction, EABI compare helpers, and non-EABI GCC comparison helpers.

## Control Flow
Moves raw float arguments from integer registers into VFP `s` registers, performs VFP `.f32` operations, returns raw bits in integer registers, and transfers VFP comparison flags to APSR for conditional returns.

## Dependencies
Depends on `<arm/asm.h>`, `<arm/vfpreg.h>`, VFP hardware, and ARM EABI/non-EABI helper naming conventions.

## Risks And Notes
Like `vfpdf.S`, correctness is tightly coupled to ABI register layout and NaN/unordered comparison semantics.
