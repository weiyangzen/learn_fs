# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevvglb.c

Implements the `vgalib` console display device for 386 PC systems using Linux/SVGAlib-style VGA access.

Key behavior:
- Defines a simple display device with a configurable `DisplayMode` parameter and 16-color focus.
- `vgalib_open` selects the configured/default VGA mode, clears the screen, infers width/height and approximate DPI when unset, and installs 16-color PC palette entries when color is available.
- `vgalib_close` restores text mode.
- RGB/color-index mapping delegates to the PC 4-bit palette helpers.
- `vgalib_fill_rectangle` clips the target and draws larger rectangles as horizontal or vertical lines, using point drawing only for very small rectangles.
- `vgalib_tile_rectangle` pre-clears fully opaque tiles before delegating to the default tiler.
- `vgalib_copy_mono` handles transparent/opaque zero/one colors, optional inversion, and bit-by-bit pixel drawing.
- `vgalib_copy_color` handles 4-bit color pixel maps nibble-by-nibble, or delegates to mono copy on monochrome devices.
- `vgalib_get_bits` reads pixels back with `vga_getpixel` and packs them according to device depth.
- `vgalib_get_params`/`put_params` expose `DisplayMode`; changing the mode closes the open device so it can be reopened with the new mode.

Dependencies:
- Uses Ghostscript device/color/parameter APIs plus `<vga.h>` SVGAlib functions such as `vga_setmode`, `vga_clear`, `vga_getcolors`, `vga_setpalette`, `vga_drawline`, `vga_drawpixel`, and `vga_getpixel`.

Research notes:
- The file states it only supports 16-color modes.
- This is another hardware/display backend inside the Ghostscript source tree, not Plan 9 filesystem or kernel logic.
