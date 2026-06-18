# File Research: sources/os/linux/linux/fs/squashfs/id.c

Maps compact on-disk uid/gid indexes to 32-bit ids.

`squashfs_get_id()` bounds-checks the index, locates the metadata block through the id index table, and reads the little-endian id.

`squashfs_read_id_index_table()` reads and validates the id table index at mount, requiring at least one id and strict monotonic metadata-block ordering.
