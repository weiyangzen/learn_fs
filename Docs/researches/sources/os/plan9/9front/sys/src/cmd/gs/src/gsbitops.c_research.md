# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsbitops.c

Purpose: Low-level bitmap and byte rectangle operations.

Bit fill/copy helpers: Defines endian-specific fill masks and implements `bits_fill_rectangle` for writing an 8x1 repeated pattern into arbitrary bit-aligned rectangles. `bits_fill_rectangle_masked` adds a source mask that preserves selected destination bits.

Replication and bounds: `bits_replicate_horizontally` expands a bitmap row pattern in place, with a byte-aligned fast path and bit-fragment fallback. `bits_replicate_vertically` copies completed tile rows downward. `bits_bounding_box` scans longword-aligned bitmap data to compute the nonzero bit bounding rectangle.

Plane conversion: `bits_extract_plane` extracts a component plane from packed pixels, with optimized CMYK-style 4-to-1 and 32-to-8 cases plus a generic sample-load/store path. `bits_expand_plane` inserts a plane into packed pixels, with optimized 8-to-32 expansion and a generic path.

Byte operations: `bytes_fill_rectangle` and `bytes_copy_rectangle` are straightforward raster-based memset/memcpy loops.

Dependencies and notes: Relies on `gxbitops.h` sample macros, bit tables from `gsbittab.h`, architecture endian/word-size macros, and Ghostscript rectangle types.
