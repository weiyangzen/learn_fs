# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevepsc.c

## Role
`gdevepsc.c` implements the `epsonc` Epson color dot-matrix printer device.

## Device and Color Mapping
- Defines compile-time default `X_DPI`/`Y_DPI` and supports 9-pin or 24-pin behavior depending on vertical resolution.
- Defines an 8-color Epson LQ-2550-style palette and maps RGB to printer color indices through `epson_map_rgb_color`; white is internally inverted with `^ 7` for calculations.
- `gs_epsonc_device` is a 3-bit color printer device using `epsc_print_page`.

## Print Path
- `epsc_print_page` allocates monochrome and output buffers, initializes printer state, optionally allocates a color scanline buffer, and scans the page in 8-line or 24-line chunks.
- Blank scanlines are accumulated into vertical skips using `ESC J`.
- For color pages, it builds monochrome masks for one ribbon color at a time and repeats passes until all colors in the band are consumed.
- Raster bytes are transposed with `gdev_prn_transpose_8x8` into the vertical column format expected by Epson graphics commands.
- It trims trailing zero bytes, uses tab commands for sufficiently large horizontal whitespace, emits graphics through `epsc_output_run`, and finishes with form feed plus reset.

## Risks and Notes
- Memory allocation failures are handled by freeing partial buffers and returning errors.
- The code assumes valid resolution combinations through graphics-mode lookup arrays but does not comprehensively validate every impossible compile-time/user combination.
- Filesystem interaction is only through the `FILE *prn_stream` supplied by Ghostscript's printer device layer.
