# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsbitmap.h

Purpose: Public client bitmap structure definitions.

Bitmap model: Documents Ghostscript’s bit-big-endian bitmap storage and scanline ordering. Defines `gs_bitmap_id` and `gs_no_bitmap_id` for cache identity, where identical IDs guarantee identical contents but not conversely.

Structures: Defines plain mutable/const bitmaps, tiled bitmaps with true repetition width/height, depth bitmaps with sample depth and component count, and tiled depth bitmaps. These client structures impose no alignment restrictions unlike corresponding `gxbitmap.h` structures.

Memory descriptors: Declares external structure descriptors and macros to publish GC pointer descriptors for bitmap variants, all tracking the `data` pointer.

Dependencies and notes: Comments state bitmap memory-management procedures live in `gspcolor.c` for historical reasons.
