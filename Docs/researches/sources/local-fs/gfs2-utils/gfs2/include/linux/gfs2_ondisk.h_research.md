# File Research: sources/local-fs/gfs2-utils/gfs2/include/linux/gfs2_ondisk.h

This header defines the GFS2 on-disk ABI structures, constants, metadata formats, flags, and block-state values used by userspace tools. It mirrors kernel-facing layout definitions with big-endian fixed-width fields.

Major contents:
- Global magic/basic-block constants and superblock address/lock constants.
- Metadata format and metatype values for superblocks, resource groups, dinodes, indirect blocks, leaves, journals, log descriptors, eattrs, and quota changes.
- Core packed-on-disk structures: `gfs2_inum`, `gfs2_meta_header`, `gfs2_sb`, `gfs2_rindex`, `gfs2_rgrp`, `gfs2_quota`, `gfs2_dinode`, `gfs2_dirent`, `gfs2_leaf`, `gfs2_ea_header`, `gfs2_log_header`, `gfs2_log_descriptor`, `gfs2_inum_range`, `gfs2_statfs_change`, `gfs2_quota_change`, and quota/resource LVB structures.
- Bitmap encoding definitions: `GFS2_NBBY`, `GFS2_BIT_SIZE`, `GFS2_BIT_MASK`, `GFS2_BLKST_*`.
- Dinode flags and directory entry conversion macros `DT2IF()`/`IF2DT()`.

Dependencies include local userspace `linux/types.h` for `__be*`/`__u*` style types and standard mode bits used by macros.

Risks and notes:
- This file is layout-critical; field order, sizes, and endian annotations must stay compatible with the filesystem format.
- Many fields preserve historical GFS1 padding/semantics, so apparent unused fields are ABI-relevant.
