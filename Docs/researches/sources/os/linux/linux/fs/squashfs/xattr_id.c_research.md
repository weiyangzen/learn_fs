# File Research: sources/os/linux/linux/fs/squashfs/xattr_id.c

Maps inode xattr ids to xattr data locations.

`squashfs_xattr_lookup()` bounds-checks the id, reads the xattr id entry from metadata via the xattr id index table, and returns xattr location, size, and count.

`squashfs_read_xattr_id_table()` reads the xattr id table header and index table, validates nonzero ids, exact table length, monotonic compressed metadata block pointers, and that the xattr data table precedes the first id block.
