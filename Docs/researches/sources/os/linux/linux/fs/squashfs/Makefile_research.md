# File Research: sources/os/linux/linux/fs/squashfs/Makefile

Builds `squashfs.o` when `CONFIG_SQUASHFS` is enabled.

Always links core objects for block I/O, caches, directories, export support, regular files, fragments, ids, inodes, name lookup, superblock handling, symlinks, decompressor dispatch, and page actors.

Conditionally links the selected file read strategy, decompressor threading implementation, xattr support, and enabled compression wrappers.
