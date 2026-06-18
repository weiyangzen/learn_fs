# File Research: sources/teaching/minix/minix/fs/ext2/buf.h

This header provides typed views over an LMFS buffer’s raw `data` pointer.

Defined data views:
- `b_data(bp)`: ordinary byte data.
- `b_ind(bp)`: block address array for indirect blocks.
- `b_bitmap(bp)`: bitmap chunk array for inode/block bitmaps.

Role:
- Central convenience layer for interpreting `struct buf` contents in ext2 code.
- Used throughout allocation, block mapping, directory parsing, read/write, and zeroing code.

Notable detail:
- `union fsdata_u` uses one-element arrays, relying on the actual buffer allocation being larger than the declared member.
