# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/inode_hash.h

## Purpose
Declares the inode tree API used by fsck link and bitmap state management.

## Main Elements
- Forward declaration for `struct inode_info`.
- Prototypes for `inodetree_find()`, `inodetree_insert()`, and `inodetree_delete()`.

## Dependencies And Integration
Includes `fsck.h` for `struct fsck_cx` and `struct lgfs2_inum`. This header is included by initialization, pass1, metawalk, link, and duplicate handling code.
