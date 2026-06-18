# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdm24.c

Implements high-resolution 24-pin dot-matrix printer drivers for NEC P6-compatible and Epson LQ850-compatible devices.

The file registers `gs_necp6_device` and `gs_lq850_device`, both 360 x 360 dpi monochrome printer devices with shared `dot24_print_page` and model-specific initialization strings.

`dot24_print_page` allocates input scanline blocks and output column buffers, initializes the printer, skips blank vertical space, gathers 24 or 48 scan lines depending on Y resolution, uses `memflip8x8` to rotate raster bits into 24-pin vertical columns, trims trailing zeros, optionally tabs across long blank horizontal runs, emits graphics runs, and ejects/reset the page.

`dot24_improve_bitmap` handles 360 dpi horizontal limitations by clearing the second-last pixel in adjacent runs so the last pixel remains printable. `dot24_output_run` writes the ESC `*` graphics command.

Risks: this is hardware-tuned raster emission. Memory allocation uses older `gs_malloc`/`gs_free` style. Correct output depends on printer emulation supporting the exact ESC/P-like commands and on `memflip8x8` semantics.
