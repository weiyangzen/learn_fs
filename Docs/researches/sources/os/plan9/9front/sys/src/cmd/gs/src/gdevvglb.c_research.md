# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevvglb.c

## Purpose
Ghostscript display driver for Linux/386 console graphics through `vgalib`, limited to 16-color modes.

## Main Concepts
- Defines `gx_device_vgalib` with a `DisplayMode` parameter.
- Registers the `vgalib` device.
- Uses svgalib calls for mode setting, palette setup, pixel drawing, line drawing, and pixel readback.

## Key Functions
- `vgalib_open`: chooses requested/default mode, clears screen, sets dimensions and resolution, initializes a 16-color palette.
- `vgalib_close`: restores text mode.
- `vgalib_map_rgb_color`, `vgalib_map_color_rgb`: delegate to PC 4-bit color mapping.
- `vgalib_fill_rectangle`: fills via lines for larger rectangles and pixels for small rectangles.
- `vgalib_tile_rectangle`: pre-fills when both tile colors are opaque, then delegates to default tiling.
- `vgalib_copy_mono`, `vgalib_copy_color`: draw source bits/nibbles pixel by pixel.
- `vgalib_get_bits`: reads pixels from the screen and packs them into Ghostscript scanline format.
- `vgalib_get_params`, `vgalib_put_params`: expose and update `DisplayMode`, closing the device before a mode change if open.

## Dependencies
Uses Ghostscript device/color/parameter APIs and external `<vga.h>` svgalib functions.

## Notable Risks
- Requires console graphics permissions and svgalib support.
- Pixel-by-pixel paths are slow.
- `vgalib_get_bits` does not range-check `y`.
- Mode switching directly affects the console and restores `TEXT` on close.

## Filesystem Relevance
No filesystem logic. This is a console display backend.
