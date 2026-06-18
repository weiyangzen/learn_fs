# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevplan9.c

This file implements the Ghostscript `plan9` printer device, producing Plan 9 compressed image/bitmap output. It is a Ghostscript printer device built on `gdevprn.h`, but contains substantial Plan 9 image format logic rather than delegating to a library.

The device type is `plan9_device`, extending `gx_device_common` and `gx_prn_device_common` with `dither`, current/last `ldepth`, and a `cmapcall` flag. `gs_plan9_device` is configured as an RGB printer device at 100 DPI with 24-bit color information and `plan9_print_page` as the page writer. The active procedure vector uses the standard printer open/output/close path plus Plan 9 color mapping procedures.

Color mapping uses 8 bits per component. `plan9_rgb2cmap` packs RGB as `0xBBGGRR` and also infers the minimal Plan 9 bitmap depth required for the page: 1-bit black/white, 4-bit grayscale, or 24-bit true color. `plan9_cmap2rgb` reverses that mapping and rejects values above 24 bits.

`plan9_print_page` reads Ghostscript raster lines through `gdev_prn_get_bits`, chooses the Plan 9 channel string (`k1`, `k4`, or `r8g8b8`), repacks rows for 1-bit or 4-bit output, pads trailing partial bytes, and writes compressed image blocks to the output `FILE`. Anti-aliasing forces at least 4-bit grayscale when needed.

The lower half of the file is an embedded Plan 9 compressed-image writer adapted from `fb/bit2enc`. It defines `WImage`, hash chains, dump buffers, a 1024-byte sliding window, and block output framing. `initwriteimage` writes the Plan 9 `compressed` image header, `gobbleline` performs LZ-style match/dump encoding, `writeimageblock` streams rows and finalizes/free the writer, and `bytesperline`/`unitsperline` mirror Plan 9 drawing-library scanline sizing.

Filesystem relevance: this is output-format code inside the Plan 9 Ghostscript tree. It writes a Plan 9 compressed bitmap stream to Ghostscript's output file path, but it is not a filesystem implementation.
