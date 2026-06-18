# File Research: sources/os/linux/linux/fs/squashfs/fragment.c

Handles SquashFS fragments, which are compressed tail-end packed datablocks.

`squashfs_frag_lookup()` maps a fragment index through the fragment index table, reads the fragment entry from metadata, returns its disk block, and decodes its compressed size.

`squashfs_read_fragment_index_table()` reads and validates the mount-time fragment index table, ensuring it does not overlap later tables and points before the table start.
