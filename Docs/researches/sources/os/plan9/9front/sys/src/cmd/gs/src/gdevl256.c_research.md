# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevl256.c

Implements the `lvga256` Ghostscript display device for Linux `vgalib` 256-color VGA modes. It registers `gs_lvga256_device` with custom open/close, RGB palette mapping, fill, tile, mono/color copy, and line drawing procedures.

Key behavior:
- `lvga256_open` initializes vgalib, selects the default VGA mode or `G320x200x256`, sets device dimensions from VGA mode, and initializes the first 64 palette entries as a coarse RGB cube.
- Dynamic colors start at palette index 64. `lvga256_map_rgb_color` maps exact coarse cube colors directly and otherwise hashes 5-bit RGB triples into `dynamic_colors`, assigning palette entries until index 255.
- If the dynamic palette is exhausted, color mapping returns `gx_no_color_index`.
- Drawing operations are direct vgalib calls: `gl_fillbox`, `gl_setpixel`, `gl_putbox`, and `gl_line`.
- `lvga256_copy_mono` handles transparent `zero`/`one` colors and pre-clears opaque rectangles before setting foreground pixels.
- `lvga256_tile_rectangle` optimizes opaque tiles by filling with `czero` and delegating the rest to `gx_default_tile_rectangle`.

Dependencies and notes:
- Requires `<vga.h>` and `<vgagl.h>`, so this is host/display-specific rather than Plan 9-specific code.
- `lvga256_map_color_rgb` is effectively a stub returning white for any color; it does not query the VGA palette.
- The dynamic color table uses linear probing with a sentinel-sized extra slot.
