# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/lost_n_found.h

## Purpose
Declares lost+found repair entry points.

## Main Elements
- `add_inode_to_lf()`: reconnect one inode into lost+found.
- `make_sure_lf_exists()`: ensure the lost+found directory exists before reconnecting.

## Dependencies And Integration
Includes `libgfs2.h` for inode types and is used by fsck passes that recover disconnected inodes.
