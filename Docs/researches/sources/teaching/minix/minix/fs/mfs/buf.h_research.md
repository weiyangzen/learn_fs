# File Research: sources/teaching/minix/minix/fs/mfs/buf.h

`buf.h` adapts libminixfs buffer objects to MFS's on-disk data layouts. It defines `union ixfer_fsdata_u`, a typed overlay for buffer data that can be interpreted as raw bytes, directory entries, V2 indirect zone entries, V2 disk inodes, or bitmap chunks.

The file then exposes accessor macros `b_data`, `b_dir`, `b_v2_ind`, `b_v2_ino`, and `b_bitmap`, each casting `b->data` to the union and selecting the appropriate member. These macros are used throughout MFS to avoid repeated casts in block, directory, inode, indirect block, and bitmap operations.

The header includes `clean.h`, so users of the buffer overlay also get the `MARKDIRTY` helper that routes dirtying through libminixfs with read-only checks.
