# File Research: sources/windows/reactos/drivers/filesystems/ntfs/blockdev.c

Read status: complete file, 380 lines.

This file provides the NTFS driver's low-level synchronous block-device helpers. It wraps lower storage-device IRPs for reads, writes, sector reads, and device I/O controls.

Key entry points:
- `NtfsReadDisk()` builds an `IRP_MJ_READ` with `IoBuildSynchronousFsdRequest()`, optionally sets `SL_OVERRIDE_VERIFY_VOLUME`, waits on pending I/O, and copies out of a temporary aligned buffer when the caller asks for an unaligned read.
- `NtfsWriteDisk()` builds `IRP_MJ_WRITE`. For unaligned writes it performs read-modify-write: rounds the target range to sector boundaries, reads the old sectors into a temporary buffer, overlays caller data, writes the full aligned buffer, then zeroes and frees it.
- `NtfsReadSectors()` converts sector/count input to byte offset/length and delegates to `NtfsReadDisk()`.
- `NtfsDeviceIoControl()` builds a synchronous device-control IRP, optionally overrides volume verification, waits for completion, and returns `IoStatus.Information` through `OutputBufferSize`.

Important dependencies:
- Kernel I/O manager: `IoBuildSynchronousFsdRequest`, `IoBuildDeviceIoControlRequest`, `IoCallDriver`, IRP stack flags.
- Memory/event helpers: `ExAllocatePoolWithTag`, `KeInitializeEvent`, `KeWaitForSingleObject`.
- NTFS constants/macros: `TAG_NTFS`, `ROUND_DOWN`, `ROUND_UP`.

Notable behavior and risks:
- The write path handles a misaligned start plus rounded length by adding another sector when needed. The read path rounds `Length` independently and allocates `RealLength + SectorSize`, but it only reads `RealLength`; for a misaligned start and sector-sized length, the final copy can require bytes beyond the read range.
- `NtfsWriteDisk()` returns success immediately for zero-length writes.
- Writes do not expose an `Override` parameter, unlike reads and device I/O controls.
