# File Research: sources/os/linux/linux/fs/nfs/blocklayout/blocklayout.h

Private header for the NFS pNFS block layout driver.

Key definitions:
- Sector/page constants: `PAGE_CACHE_SECTORS`, `PAGE_CACHE_SECTOR_SHIFT`, `SECTOR_SIZE`.
- Limits for UUIDs, devices, and UUID length.
- `struct pnfs_block_volume`: represents simple, slice, concat, stripe, and SCSI volume descriptions.
- `struct pnfs_block_dev_map`: maps a logical range to a block device and disk offset.
- `struct pnfs_block_dev`: pNFS device node with hierarchy, block device file, disk offset, flags, persistent reservation key, and map callback.
- `struct pnfs_block_extent`: sector-granular file extent with device, file offset, length, volume offset, state, and commit tags.
- `struct pnfs_block_layout`: layout header plus read/write extent trees, lock, SCSI flag, and last-written byte.
- rpc_pipefs message structures and constants.

Important helpers:
- `BLK_LO2EXT()`.
- `BLK_LSEG2EXT()`.

Declared cross-file APIs:
- Device registration/allocation/free from `dev.c`.
- Extent tree insert/remove/lookup/commit helpers from `extent_tree.c`.
- Device resolution and pipefs init/cleanup from `rpc_pipefs.c`.

Role:
- Defines the shared data model used by `blocklayout.c` to translate NFS pNFS extents into local block-device I/O.
