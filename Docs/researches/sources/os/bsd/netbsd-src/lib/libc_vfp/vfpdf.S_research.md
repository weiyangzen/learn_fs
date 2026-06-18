# File Research: sources/os/bsd/netbsd-src/lib/libc_vfp/vfpdf.S

## Purpose
Implements double-precision soft-float ABI helpers using ARM VFP instructions.

## Main Entry Points
Provides double add/subtract/multiply/divide/negate, float-to-double, double-to-signed/unsigned int, int-to-double, unsigned-int-to-double, ARM EABI reverse subtraction, EABI compare helpers, and non-EABI GCC comparison helpers.

## Control Flow
Macros move double arguments between ARM integer registers and VFP `d` registers, accounting for ARM endian order. Arithmetic and conversions use VFP instructions, and results are moved back to integer registers. EABI symbol names are mapped to GCC helper names when `__ARM_EABI__` is defined.

## Dependencies
Depends on `<arm/asm.h>`, VFP hardware, ARM EABI/non-EABI calling conventions, and APSR/FPSCR condition flag transfer.

## Risks And Notes
Comparison helpers depend on exact interpretation of VFP condition flags, especially unordered NaN cases. Endian-specific argument movement is critical.
