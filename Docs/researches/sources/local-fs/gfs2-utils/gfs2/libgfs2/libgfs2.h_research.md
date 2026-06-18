# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/libgfs2.h

This is the main public/internal libgfs2 header.

Content:
- Endian conversion macros for big/little endian hosts.
- Metadata type enum and metadata/field descriptor structures.
- Device, bitmap, resource-group, buffer-head, inum, inode, metadata-directory, superblock, log-header, dirent, leaf, and metapath structures.
- Defaults and bounds for block size, journal size, resource group size, lock protocol, and filesystem format.
- Prototypes for metadata description, buffer I/O, device geometry, bitmap operations, fs ops, misc helpers, recovery, rgrp management, structure builders, superblock/rindex I/O, disk hash, and ondisk conversion.

Integration role:
- Central include for most libgfs2 and mkfs/grow/jadd code.
- Bridges Linux `gfs2_ondisk.h` structures with userland in-core representations.

Risk notes:
- Struct layout and prototypes define broad cross-file contracts.
- Endian macros depend on `__BYTE_ORDER`.
- `LGFS2_SB_ADDR(sdp)` depends on computed `sd_fsb2bb_shift`.
- Many functions expose raw block numbers and direct metadata mutation, so caller invariants are important.
