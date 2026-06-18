# File Research: sources/os/linux/linux-stable/fs/befs/io.h

This header declares the BeFS block-address read helper.

Export:
- `befs_bread_iaddr(struct super_block *sb, befs_inode_addr iaddr)`

Integration:
- Implemented in `io.c`.
- Used by `datastream.c`.

Risk notes:
- The returned `buffer_head` must be released by callers.
