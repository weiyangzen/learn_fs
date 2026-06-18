# File Research: sources/os/linux/linux/fs/nfsd/blocklayoutxdr.h

Defines NFSD pNFS block/SCSI layout wire helper structures and XDR helper prototypes.

Key behavior:
- Defines `PNFS_BLOCK_LAYOUT4_SIZE`, the wire size of a layout with zero extents.
- Defines `struct pnfs_block_extent` with device ID, file offset, length, storage offset, and extent state.
- Defines `struct pnfs_block_range` for file offset/length ranges.
- Defines flexible-array `struct pnfs_block_layout` for returned extent arrays.
- Defines `PNFS_BLOCK_UUID_LEN` as a defensive upper bound for simple-volume UUID/signature length.
- Defines `struct pnfs_block_volume` for simple and SCSI volume encodings.
- Defines flexible-array `struct pnfs_block_deviceaddr` for device-address volume lists.
- Declares block getdeviceinfo/layoutget encoders and block/SCSI layoutupdate decoders.

Important interactions:
- Included by `blocklayout.c` and `blocklayoutxdr.c`.
- Provides the shared in-memory representation used between pNFS layout logic and XDR encode/decode routines.
