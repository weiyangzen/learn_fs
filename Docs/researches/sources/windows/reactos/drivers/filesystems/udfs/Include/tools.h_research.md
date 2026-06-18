# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/tools.h

## Purpose
Provides byte-order, MSF/LBA, packet-addressing, min/max, and simple lock helper macros used across UDFS.

## Main Contents
- Defines `FOUR_BYTE`.
- Provides `AcquireXLock`, either x86 `xchg` based or simple assignment fallback.
- Declares x86 helper routines and maps macros such as `MOV_DD_SWP`, `MOV_DW_SWP`, `REVERSE_DD`, `REVERSE_DW`, `MOV_MSF`, `MOV_MSF_SWP`, and `XCHG_DD`.
- Provides generic C macro implementations when the x86 helper path is unavailable.
- Defines `MSF_TO_LBA`, `PacketFixed2Variable`, `PacketVariable2Fixed`, `WAIT_FOR_XXX_EMU_DELAY`, `max`, `min`, and a fallback `offsetof`.

## Notable Risks
- `AcquireXLock` is only atomic in the x86/CrossNT helper path; the generic fallback is not atomic.
- `CONV_TO_LL` appears suspicious because `Byte3` is shifted by 8 rather than 24.
- Generic macros evaluate arguments through address-taking and local pointer casts, so callers should avoid expressions with side effects.
