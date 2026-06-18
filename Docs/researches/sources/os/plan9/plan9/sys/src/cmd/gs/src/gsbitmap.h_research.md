# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsbitmap.h

Purpose: Defines public/client bitmap structures for Ghostscript APIs that do not require aligned bitmap data.

Key interfaces: `gs_bitmap_id`, `gs_no_bitmap_id`, `gs_bitmap`, `gs_const_bitmap`, `gs_tile_bitmap`, `gs_const_tile_bitmap`, `gs_depth_bitmap`, `gs_const_depth_bitmap`, `gs_tile_depth_bitmap`, `gs_const_tile_depth_bitmap`, and structure descriptor declaration/definition macros.

Behavior: Bitmaps are bit-big-endian byte sequences with y=0 first. Tile bitmaps record true replicated dimensions. Depth variants add bits-per-sample and component count for interleaved data. Structure descriptors are declared here but implemented through macros expected in `gspcolor.c`.

Dependencies: Uses `gsstype.h`, `gs_id`, `gs_int_point`, and Ghostscript structure descriptor macros.

Risks and notes: Comments warn that core aligned bitmap structures in `gxbitmap.h` have identical contents but stricter alignment assumptions; casting unaligned data to aligned structures is only safe when alignment is known.
