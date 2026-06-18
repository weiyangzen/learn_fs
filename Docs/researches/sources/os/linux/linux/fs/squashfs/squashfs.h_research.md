# File Research: sources/os/linux/linux/fs/squashfs/squashfs.h

Central internal header for SquashFS implementation declarations.

Defines trace/error/warning macros, `SQUASHFS_READ_PAGES`, the decompressor-thread-ops interface, and prototypes for block reads, caches, decompressor setup, table readers, inode/fragment/id/xattr lookup, file helpers, and exported VFS operation tables.

It connects the separately compiled strategy files and conditional decompressor threading objects to the rest of the filesystem.
