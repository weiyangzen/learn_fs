# File Research: sources/local-fs/erofs-utils/lib/metabox.c

This file implements metadata-zone and metabox staging managers.

Core type:
- `struct erofs_metamgr` holds a temporary `erofs_vfile` and its own `erofs_bufmgr`.

Lifecycle:
- `erofs_metamgr_init()` creates a temporary file and initializes a buffer manager against it.
- `erofs_metamgr_exit()` exits the buffer manager, closes the temp vfile, and frees the manager.
- `erofs_metadata_init()` creates `sbi->m2gr` when `metazone_startblk == EROFS_META_NEW_ADDR`, and creates `sbi->mxgr` when the superblock has metabox enabled.
- `erofs_metadata_exit()` releases both managers.

Access:
- `erofs_metadata_bmgr(sbi, mbox)` returns the metazone or metabox buffer manager if present.

Flush paths:
- `erofs_metabox_iflush()` flushes metabox buffers, checks if the temp file has data, imports it as a special inode from fd, records `sbi->metabox_nid`, and drops the inode.
- `erofs_metazone_flush()` allocates a DATA area in the main image, flushes metazone buffers, balloons the destination buffer head to the metazone length, copies staged metadata into the main image, drops the buffer head, and adjusts `sbi->meta_blkaddr`.

Important behavior:
- Metazone data is staged separately and later copied into the main image.
- Metabox content becomes a regular special inode generated from the temp fd.
- `sbi->meta_blkaddr` is set to `EROFS_META_NEW_ADDR` during new metazone initialization.

Risks / notes:
- `erofs_metazone_flush()` returns success even if the copy loop breaks only after a negative `ret`? It checks and breaks, but final return is `0`; the negative copy result path should be reviewed.
- Temporary file and buffer manager lifetime is tied to `sbi->m2gr` / `sbi->mxgr`.
