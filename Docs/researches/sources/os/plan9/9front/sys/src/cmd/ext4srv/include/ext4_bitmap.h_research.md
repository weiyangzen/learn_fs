# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_bitmap.h

Bitmap helper header for allocation bitmaps.

Key behavior:
- Provides inline little-bit-order set, clear, is-set, and is-clear operations.
- Declares `ext4_bmap_bits_free` for clearing bit ranges.
- Declares `ext4_bmap_bit_find_clr` for finding the first clear bit in a bounded range and reporting no-space status.

Notable dependencies:
- Includes `ext4_config.h`.
- Implemented by `ext4_bitmap.c`; used by block and inode allocation.

Research notes:
- Helpers do not bounds-check bitmap memory; callers supply valid bit ranges.
