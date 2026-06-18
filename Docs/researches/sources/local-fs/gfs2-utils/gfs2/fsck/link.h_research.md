# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/link.h

## Purpose
Declares link-count tracking state and APIs shared across fsck passes.

## Main Elements
- Extern maps `nlink1map` and `clink1map`.
- Increment result enum: `INCR_LINK_BAD`, `INCR_LINK_GOOD`, `INCR_LINK_INO_MISMATCH`, `INCR_LINK_CHECK_ORIG`.
- Prototypes for one-bit map updates and link count set/increment/decrement helpers.

## Dependencies And Integration
Includes `fsck.h` for fsck context, bitmap, inode, and inum types. Used by pass1, pass1b, lost+found, metawalk, and main cleanup.
