# File Research: sources/windows/reactos/sdk/lib/fslib/ext2lib/Disk.c

This file provides low-level device and volume I/O helpers for the ext2 formatter.

Core responsibilities:
- `Ext2StatusToString` maps many NTSTATUS constants to diagnostic names.
- `Ext2ReadDisk` and `Ext2WriteDisk` perform sector-aligned raw disk I/O, allocating a temporary heap buffer when caller offset/length are not sector aligned.
- `Ext2GetMediaInfo` queries drive geometry and partition information with disk IOCTLs.
- `Ext2LockVolume`, `Ext2UnLockVolume`, and `Ext2DisMountVolume` wrap volume FSCTLs.
- `Ext2OpenDevice` opens the target volume/device with read/write/synchronous access; `Ext2CloseDevice` closes the stored handle.

Important behavior:
- Raw writes read the enclosing sector range first when modifying only a partial sector, then overlay caller data before writing the aligned range.
- File-backed I/O paths are present but disabled with `#if 0`.
- The `SECTOR_SIZE` macro resolves through `Ext2Sys->DiskGeometry.BytesPerSector`, so callers must query media info before relying on it.

Risk points:
- `Ext2OpenDevice` returns the original `Status` even if `Iosb.Status` fails after a successful call.
- Partial-sector buffering depends on geometry being valid and heap allocation succeeding.
- The huge hard-coded status table is maintenance-heavy and may lag newer status codes.
- Volume lock/dismount failures are logged but cleanup decisions are left to higher-level formatter code.
