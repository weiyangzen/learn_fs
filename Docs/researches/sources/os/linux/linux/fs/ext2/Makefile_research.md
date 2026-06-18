# File Research: sources/os/linux/linux/fs/ext2/Makefile

Read status: complete, 16 lines.

This Makefile builds the ext2 filesystem object.

Key responsibilities:
- Builds `ext2.o` when `CONFIG_EXT2_FS` is enabled.
- Core object list: `balloc.o`, `dir.o`, `file.o`, `ialloc.o`, `inode.o`, `ioctl.o`, `namei.o`, `super.o`, `symlink.o`, and `trace.o`.
- Adds include path for tracepoint infrastructure with `CFLAGS_trace.o := -I$(src)`.
- Conditionally adds xattr, ACL, and security-label implementation files.

Research notes:
- The Makefile shows ext2’s major implementation split: block allocation, inode allocation, inode/block mapping, directory format handling, VFS name operations, file operations, mount/superblock handling, symlinks, and tracepoints.
