# File Research: sources/teaching/xv6-riscv/mkfs/mkfs.c

Host-side tool that creates an xv6 filesystem image.

Important behavior:
- Computes filesystem layout from `FSSIZE`, `LOGBLOCKS`, inode blocks, and bitmap blocks.
- Writes zeroed blocks, then writes the superblock.
- Allocates root inode, creates `.` and `..`, and appends requested input files into the root directory.
- Strips leading `user/` and leading `_` from installed program names.
- Uses `xshort()` and `xint()` to emit little-endian on-disk fields.
- `ialloc()` initializes on-disk inodes.
- `iappend()` allocates direct or indirect blocks and appends file data.
- `balloc()` writes the bitmap marking all used blocks.

Filesystem relevance: this tool must exactly match `kernel/fs.h` and the kernel’s inode/block interpretation. It builds the initial root filesystem consumed by `fsinit()`, path lookup, and `exec("/init")`.
