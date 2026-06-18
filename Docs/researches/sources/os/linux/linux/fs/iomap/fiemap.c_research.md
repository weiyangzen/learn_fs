# File Research: sources/os/linux/linux/fs/iomap/fiemap.c

Provides iomap-backed FIEMAP and legacy bmap support.

Key functions:
- `iomap_to_fiemap()` converts one `struct iomap` into FIEMAP extent flags and emits it with `fiemap_fill_next_extent()`. Holes are skipped; delalloc, unwritten, inline, merged, and shared mappings become corresponding FIEMAP flags.
- `iomap_fiemap_iter()` delays emission by one mapping so the final mapping can be marked `FIEMAP_EXTENT_LAST`.
- `iomap_fiemap()` prepares FIEMAP, iterates mappings with `IOMAP_REPORT`, emits the saved final extent, and treats `-ENOENT` as “no mapping”.
- `iomap_bmap()` implements the old `->bmap` interface by flushing dirty mapping pages, asking the filesystem for an `IOMAP_REPORT` mapping of one block, and returning the mapped disk block or zero.

This file is a reporting layer: it does not allocate or submit I/O. It depends on filesystem `iomap_ops` for mapping lookup and on `iomap_iter()` for range traversal.
