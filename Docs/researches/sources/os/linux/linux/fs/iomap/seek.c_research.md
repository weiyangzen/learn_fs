# File Research: sources/os/linux/linux/fs/iomap/seek.c

Implements iomap-based `SEEK_HOLE` and `SEEK_DATA`.

Key functions:
- `iomap_seek_hole()` validates `pos` against `i_size`, iterates mappings with `IOMAP_REPORT`, and returns the first hole position or EOF.
- `iomap_seek_data()` similarly returns the first data position or `-ENXIO`.
- For `IOMAP_UNWRITTEN`, both helpers consult `mapping_seek_hole_data()` over the page cache so dirty cached data inside unwritten extents is considered.
- `IOMAP_HOLE` is immediately a hole and skipped for data.
- Other mapping types are treated as data for `SEEK_DATA` and skipped for `SEEK_HOLE`.

This file layers POSIX seek behavior over filesystem mappings while preserving page-cache-visible data in unwritten regions.
