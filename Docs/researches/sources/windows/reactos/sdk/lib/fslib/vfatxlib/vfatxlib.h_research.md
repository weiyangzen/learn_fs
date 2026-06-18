# File Research: sources/windows/reactos/sdk/lib/fslib/vfatxlib/vfatxlib.h

Internal header for the ReactOS VFATX library.

Key elements:
- Includes ReactOS user-mode NDK types, process/thread/loader types, I/O functions, and FMIFS APIs.
- Defines packed `FATX_BOOT_SECTOR`, a 4096-byte structure with signature, volume ID, sectors per cluster, FAT count, unknown field, and unused padding.
- Defines VFATX `FORMAT_CONTEXT`.
- Declares `FatxFormat` and `VfatxUpdateProgress`.

Dependencies:
- Used by both `fatx.c` and `vfatxlib.c`.

Research notes:
- FATX boot-sector layout is much simpler than FAT12/16/32 BPBs.
- The header exposes only formatter internals; no FATX checking API is declared beyond the exported implementation signature in `vfatxlib.c`.
