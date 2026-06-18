# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/phys_lib.cpp

## Purpose
Implements UDFS physical-device I/O for optical and disk media: low-level reads/writes, write preparation, retry/error recovery, track-map discovery, block-size detection, device-driver reset, speed control, caching mode setup, and unaligned data access.

## Main Responsibilities
- `UDFTRead` and `UDFTWrite` issue synchronous physical reads/writes through `UDFPhReadSynchronous` / `UDFPhWriteVerifySynchronous`, with optional relocation-map handling under `_BROWSE_UDF_`.
- `UDFPrepareForWriteOperation` configures optical write parameters, packet mode, random-access mode, OPC, MRW mode, and background-format continuation before writes.
- `UDFRecoverFromError` interprets low-level CDRW/SCSI sense data and decides whether to retry, sync cache, reset/reinitialize the lower driver, delay for in-progress operations, mark bad blocks, or fail.
- `UDFReadDiscTrackInfo`, `UDFReadAndProcessFullToc`, and `UDFUseStandard` populate `VCB` media layout fields from CDRW-specific IOCTLs, full TOC, or standard CDROM TOC fallback.
- `UDFGetBlockSize` and `UDFGetDiskInfo` establish block size, last LBA, media class, writable/read-only flags, compatibility flags, cache sizing, track map, and speed/caching policy.
- `UDFReadData`, `UDFWriteData`, `UDFReadInSector`, and `UDFWriteInSector` bridge byte-range requests to sector-aligned physical I/O and write-cache access.

## Important Data/State
The file mutates many `PVCB` fields defined in `udf_common.h`: block size, track map, media class, `LastLBA`, `LastPossibleLBA`, `NWA`, `VCBFlags`, `CompatFlags`, `BSBM_Bitmap`, write cache, speed buffers, OPC state, MRW state, and last-error buffers.

## Build Modes
Behavior is heavily conditional:
- `_BROWSE_UDF_` enables relocation, bad-block sparing, verify-cache recovery, write cache, raw UDF browsing, unaligned read/write helpers, and fixed-packet/MRW addressing workarounds.
- `UDF_FORMAT_MEDIA` adds formatter-specific media probing, output, and `fms` policy handling.
- `UDF_READ_ONLY_BUILD` disables physical write paths.
- `UDF_ASYNC_IO` contains an unused async read path.

## Notable Risks
- The code uses extensive stateful device heuristics and retry loops around optical media behavior; regressions can affect mounting, formatting, or data integrity.
- Several pointer increments cast `Buffer` through `uint32*`, reflecting old 32-bit assumptions.
- Many IOCTL buffers are reused through type punning.
- Error recovery can mark bad blocks and alter free/zero bitmaps, so call context and lock ownership matter.
