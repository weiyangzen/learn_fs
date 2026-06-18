# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpcfb.c

This file implements Ghostscript IBM PC EGA/VGA/SVGA16 framebuffer devices. It directly manipulates VGA/EGA graphics registers and frame-buffer memory through helpers declared in `gdevpcfb.h`. It is platform/display-driver code, not filesystem code.

The device prototypes are `gs_ega_device`, `gs_vga_device`, and `gs_svga16_device`, with `svga16` exposing a `DisplayMode` parameter through `svga16_get_params` and `svga16_put_params`. `ega_open` adjusts resolution according to the selected video mode, saves BIOS/display state once, initializes signal handling, sets the graphics mode, and enables all VGA planes. `ega_close` restores the saved state.

Color mapping can be compiled as monochrome, one-bit-per-component, or full 4-bit EGA mapping depending on `ega_bits_of_color`. The active configuration in the header uses `ega_bits_of_color 2`, so it maps through `pc_4bit_map_rgb_color`.

The central raster operation type is `rop_params`, shared with optional assembly routines. The C fallback routines include `cmemsetcol`, `cmemsetrect`, `cmemrwcol`, `cmemrwcol0`, and `cmemrwcol2`, which write columns/rectangles and shifted source data into planar VGA memory.

Drawing primitives include `ega_write_dot`, `ega_copy_mono`, `ega_copy_color`, `ega_fill_rectangle`, and `ega_tile_rectangle`. `ega_copy_mono` contains detailed case analysis for black, white, transparent, and arbitrary EGA colors. It chooses VGA logical functions, set/reset maps, masks, and sometimes two passes to implement transparent source or nontrivial color combinations. `ega_copy_color` copies 4-bit pixel data into planar memory by selecting bit masks and using VGA latches. `ega_tile_rectangle` has an optimized path for byte-aligned monochrome tiles with opaque colors and falls back to Ghostscript’s default tiler for harder cases.

`ega_get_bits` reads four VGA planes back into a chunky 4-bit-per-pixel row using a lookup table. Fill helpers `fill_rectangle` and `fill_row_only` optimize masked byte/column writes and special black/white one-row cases.
