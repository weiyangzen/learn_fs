# File Research: sources/os/linux/linux-stable/fs/iomap/seek.c

Provides generic `SEEK_HOLE` and `SEEK_DATA` operations using iomap mappings plus page-cache inspection for unwritten extents.

Key paths:
- `iomap_seek_hole()` validates `pos`, iterates to EOF with `IOMAP_REPORT`, and returns either the first hole/unwritten cached hole or EOF.
- `iomap_seek_data()` validates `pos`, iterates to EOF, and returns the first mapped data or page-cache data inside unwritten extents.
- `iomap_seek_hole_iter()` treats holes as holes, mapped extents as data, and uses `mapping_seek_hole_data(..., SEEK_HOLE)` inside unwritten mappings.
- `iomap_seek_data_iter()` skips holes, reports mapped/inline/delalloc-style mappings as data, and uses `mapping_seek_hole_data(..., SEEK_DATA)` for unwritten mappings.

Important behavior:
- Positions before 0 or at/after i_size return `-ENXIO`.
- Unwritten extents can contain cached dirty data, so page-cache checks refine the on-disk mapping answer.
