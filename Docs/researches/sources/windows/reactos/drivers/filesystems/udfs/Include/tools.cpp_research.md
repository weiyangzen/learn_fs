# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/tools.cpp

## Purpose
Implements x86 assembly helpers declared by `tools.h`.

## Main Contents
Under `_X86_`, defines naked `__fastcall` routines for:
- Moving 32-bit and 16-bit values with byte swapping.
- Reversing 32-bit and 16-bit values in place.
- Moving swapped 16-bit values into 32-bit storage.
- Copying MSF byte triplets with and without swapping.
- Exchanging DWORD values.

## Notes
For non-x86 builds, the equivalent behavior is macro-defined in `tools.h`; this `.cpp` contributes only the x86 optimized implementations.
