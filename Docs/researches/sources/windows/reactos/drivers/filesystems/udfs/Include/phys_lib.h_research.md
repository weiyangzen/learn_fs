# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/phys_lib.h

## Purpose
Public declarations and flags for the physical I/O layer implemented in `phys_lib.cpp`.

## Main Contents
- Declares low-level APIs: `UDFTRead`, `UDFTWrite`, verify wrappers, disk-info discovery, block-size detection, read/write preparation, NWA updates, and driver reset.
- Defines physical I/O flags such as `PH_TMP_BUFFER`, `PH_VCB_IN_RETLEN`, `PH_LOCK_CACHE`, `PH_EX_WRITE`, and `PH_IO_LOCKED`.
- Defines `UDFReadSectors` as a macro that prefers `WCacheReadBlocks__` when the fast cache is initialized and IRQL allows it, otherwise falls back to `UDFTRead`.
- Exposes unaligned read/write helpers and write-sector helpers, with write declarations gated by `UDF_READ_ONLY_BUILD`.

## Dependencies
Requires UDFS core types such as `PVCB`, `PDEVICE_OBJECT`, `OSSTATUS`, `PSIZE_T`, and write-cache functions/macros from the surrounding include set.

## Notes
This header is not standalone; it is meant to be included after the UDFS environment and common type headers are available.
