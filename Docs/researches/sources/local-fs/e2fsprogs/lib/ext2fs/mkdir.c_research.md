# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/mkdir.c

Implements `ext2fs_mkdir2()` and compatibility wrapper `ext2fs_mkdir()`. It allocates a directory inode and either a real data block or inline directory data depending on filesystem features and inode number.

The function builds a new directory template, initializes mode, size, extents/inline-data flags, link count, timestamps via `ext2fs_write_new_inode`, and then links the directory into its parent with `ext2fs_link()` after checking for name collisions.

It updates block/inode allocation accounting and increments the parent directory link count. Cleanup paths drop allocation stats if linking or inode writing fails after allocation, but they do not perform a full semantic rollback of all possible on-disk writes.
