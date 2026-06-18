# File Research: sources/teaching/minix/minix/fs/mfs/cache.c

This file provides MFS-specific wrappers around libminixfs buffer and block allocation facilities. The actual buffer cache is in libminixfs; this file supplies policy and filesystem bitmap integration.

`get_block` wraps `lmfs_get_block`, panicking on I/O errors other than `ENOENT` for `PEEK` requests. This reflects MFS's lack of pervasive recoverable read-error handling and prevents unchecked corruption paths.

`alloc_zone` allocates a data zone from the zone bitmap. It translates between bitmap bit numbers and on-disk zone numbers using `s_firstdatazone`, starts near the caller's hint or the superblock search cursor, updates `s_zsearch`, reports `ENOSPC`, and suppresses repeated "No space" messages after the first failure. `free_zone` reverses the mapping, clears the zone bitmap bit, updates the search cursor, and calls `lmfs_free_block` so cached data and VM block-to-inode associations are invalidated. The implementation asserts `s_log_zone_size == 0`, matching MFS's dropped support for multi-block zones.
