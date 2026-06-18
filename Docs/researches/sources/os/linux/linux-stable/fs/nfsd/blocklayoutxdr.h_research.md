# File Research: sources/os/linux/linux-stable/fs/nfsd/blocklayoutxdr.h

Purpose: Declares pNFS block/SCSI layout wire helper structures and XDR functions.

Key responsibilities:
- Defines wire-size constants for block layout and UUID limits.
- Defines in-memory representations:
  - `pnfs_block_extent`,
  - `pnfs_block_range`,
  - counted flexible `pnfs_block_layout`,
  - `pnfs_block_volume`,
  - counted flexible `pnfs_block_deviceaddr`.
- Declares getdeviceinfo/layoutget encoders and block/SCSI layoutupdate decoders.

Integration:
- Shared by `blocklayout.c` and `blocklayoutxdr.c`.
- Includes block device and NFSD NFSv4 XDR definitions.

Risks and notes:
- UUID length is capped at 128 as an implementation guard, not a protocol limit.
- SCSI designator buffer is fixed at 256 bytes.
