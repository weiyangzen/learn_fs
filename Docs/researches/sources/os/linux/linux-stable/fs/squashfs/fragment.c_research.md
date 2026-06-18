# File Research: sources/os/linux/linux-stable/fs/squashfs/fragment.c

## Summary
Handles Squashfs fragment table lookup for tail-end packed file blocks.

## Key APIs
- `squashfs_frag_lookup()`.
- `squashfs_read_fragment_index_table()`.

## Important Behavior
`squashfs_frag_lookup()` maps a fragment number to its compressed fragment block start and compressed size by reading a fragment entry from the compressed fragment table via the mount-cached fragment index.

`squashfs_read_fragment_index_table()` reads the uncompressed fragment-index table and validates that it does not overlap the next table and that the first fragment metadata block precedes the index table.

## Risks
Fragment indices are used by inode parsing and file tail reads. A bad fragment table can otherwise redirect reads to invalid compressed blocks, so mount-time bounds checks are important.
