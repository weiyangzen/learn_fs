# File Research: sources/teaching/xv6-public/mkfs.c

Host-side filesystem image builder for xv6.

Key behavior:
- Computes filesystem layout from `FSSIZE`, `LOGSIZE`, `NINODES`, inode blocks, and bitmap blocks.
- Initializes the image with zeroed sectors, writes the superblock, allocates root inode, and creates `.`/`..`.
- Adds each input file as a root directory entry, stripping leading `_` from user program names.
- Allocates direct and indirect blocks in `iappend`, writes file data, and updates inode sizes.
- Rounds root directory size to a full block.
- Writes the bitmap for all allocated blocks.
- Converts all on-disk integer fields to little-endian with `xshort`/`xint`.

Important interactions:
- Shares `fs.h`, `stat.h`, `param.h`, and `types.h` with the kernel to keep on-disk format aligned.
- Assumes host `int` is 4 bytes.
