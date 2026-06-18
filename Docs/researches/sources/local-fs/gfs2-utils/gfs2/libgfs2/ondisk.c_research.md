# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/ondisk.c

This file converts selected GFS2 on-disk structures between big-endian disk format and libgfs2 in-core structures.

Public APIs:
- `lgfs2_inum_in/out()`
- `lgfs2_sb_in/out()`
- `lgfs2_rindex_in/out()`
- `lgfs2_rgrp_in/out()`
- `lgfs2_dinode_in/out()`
- `lgfs2_dirent_in/out()`
- `lgfs2_leaf_in/out()`

Behavior:
- Reads and writes superblock fields, inums, resource-group index fields, resource-group fields, dinode fields, dirent fields, and leaf fields.
- Output helpers set metadata header magic/type/format where applicable.
- `lgfs2_rgrp_out()` recomputes resource group CRC after writing fields.

Integration role:
- Used throughout libgfs2 for reading existing metadata and writing modified/created metadata.
- Provides the endian boundary between userland native structs and Linux GFS2 on-disk structs.

Risk notes:
- Every field conversion must remain synchronized with on-disk structure definitions.
- `lgfs2_leaf_in/out()` assumes leaf hint fields exist in the compiled kernel header layout.
- `lgfs2_dinode_out()` writes in-core header values rather than hardcoding them, so inode initialization must set those correctly.
