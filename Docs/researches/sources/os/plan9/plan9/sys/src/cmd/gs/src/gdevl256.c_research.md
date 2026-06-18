# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevl256.c

Implements the `lvga256` Ghostscript display device for Linux VGA/vgalib 256-color modes. It opens vgalib, selects the default VGA mode or `G320x200x256`, sets device dimensions from the actual mode, initializes the first 64 palette entries as a compatibility color cube, and manages remaining palette slots dynamically.

Main entry points are `lvga256_open`, `lvga256_close`, `lvga256_map_rgb_color`, `lvga256_map_color_rgb`, `lvga256_fill_rectangle`, `lvga256_tile_rectangle`, `lvga256_copy_mono`, `lvga256_copy_color`, and `lvga256_draw_line`. The device descriptor is `gs_lvga256_device`.

The dynamic color allocator stores 5-bit RGB triples in a fixed open-addressed hash table and assigns VGA palette indices from 64 through 255. When the palette is exhausted, RGB mapping returns `gx_no_color_index`.

Rendering is direct vgalib/`vgagl`: `gl_fillbox`, `gl_putbox`, `gl_setpixel`, and `gl_line`. This makes the file platform-specific and unsuitable for non-Linux/non-vgalib builds without conditional exclusion.

Notable limitation: `lvga256_map_color_rgb` is effectively a stub that always returns white, so reverse color mapping is not faithful.
