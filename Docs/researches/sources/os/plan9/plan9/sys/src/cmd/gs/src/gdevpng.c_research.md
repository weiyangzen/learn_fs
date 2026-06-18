# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpng.c

This file implements Ghostscript PNG output devices using libpng. It defines printer-style devices for monochrome, indexed color, grayscale, RGB, high-depth RGB, and RGBA-with-coverage output.

The standard devices are:

- `pngmono`: 1-bit grayscale.
- `png16`: 4-bit palette color using PC-style 4-bit mapping.
- `png256`: 8-bit palette color using PC-style 3/3/2 mapping.
- `pnggray`: 8-bit grayscale.
- `png16m`: 24-bit RGB.
- `png48`: 48-bit RGB.
- `pngalpha`: 32-bit RGBA, with alpha representing pixel coverage rather than full PDF transparency.

All normal devices use `png_print_page`, which allocates one raster row, creates libpng write/info structures, initializes output to the Ghostscript printer `FILE`, writes pHYs resolution metadata, selects PNG color type/bit depth from `pdev->color_info.depth`, emits a palette when needed, adds a `Software` text chunk, then streams scanlines from `gdev_prn_copy_scan_lines` to `png_write_rows`. It handles alpha inversion for `pngalpha`, mono inversion for 1-bit output, and byte swapping for 16-bit RGB on little-endian platforms.

`pngalpha` has its own device structure containing the original fill-rectangle procedure and a `BackgroundColor` parameter. `pngalpha_open` installs a custom buffer-device creation hook and intercepts full-page white fills. `pngalpha_fill_rectangle` converts a full-page white erase into a transparent fill. `pngalpha_encode_color` stores pixels as `0xRRGGBB00`, with inverted coverage in the low byte so fully opaque white does not collide with `gx_no_color_index`. `pngalpha_copy_alpha` implements coverage compositing into an RGBA memory buffer by reading old pixels, computing new coverage, blending color components, and writing accumulated pixels back.

Filesystem relevance: output file serialization only. The code writes PNG data through Ghostscript's printer output file abstraction; it does not implement storage or filesystem behavior.
