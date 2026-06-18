# File Research: sources/os/linux/linux-stable/fs/iomap/fiemap.c

Provides generic iomap-backed FIEMAP and legacy bmap support.

Key paths:
- `iomap_to_fiemap()` converts `IOMAP_*` mapping types and flags into `FIEMAP_EXTENT_*` flags, skipping holes.
- `iomap_fiemap_iter()` delays emitting the previous extent until the next non-hole mapping, allowing final extent marking at the end.
- `iomap_fiemap()` prepares the request with `fiemap_prep()`, iterates mappings with `IOMAP_REPORT`, emits the last extent with `FIEMAP_EXTENT_LAST`, and treats `-ENOENT` as no mapping.
- `iomap_bmap()` implements old `->bmap`, flushes dirty page cache first, maps one block through iomap, and returns 0 on errors per legacy API.

Important details:
- DELALLOC is reported as both delayed allocation and unknown.
- UNWRITTEN, INLINE, MERGED, and SHARED iomap state maps directly to FIEMAP flags.
- `iomap_bmap()` intentionally aborts after the first mapping by leaving `iter.status` unset.
