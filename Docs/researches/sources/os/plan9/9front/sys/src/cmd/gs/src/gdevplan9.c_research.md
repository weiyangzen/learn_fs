# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevplan9.c

Ghostscript printer device that writes Plan 9 compressed bitmap images. It defines the `plan9` device, Plan 9-style point/rectangle helpers, RGB color mapping, a `Dither` parameter, page raster conversion, and an embedded Plan 9 image compressor adapted from `fb/bit2enc`.

Key behavior:
- `gs_plan9_device` is a 24-bit RGB printer device at 100 DPI with zero margins.
- `plan9_rgb2cmap` maps Ghostscript RGB values into packed low-byte red, middle-byte green, high-byte blue pixels and watches requested colors to infer a Plan 9 output depth.
- `plan9_cmap2rgb` decodes packed colors back to Ghostscript RGB values and rejects indexes above 24 bits.
- `plan9_get_params` and `plan9_put_params` expose a boolean-ish `Dither` parameter, although the current page writer does not visibly use it for a dithering algorithm.
- `plan9_open` initializes Plan 9 color tables through `init_p9color()` and opens the generic printer backing device.
- `plan9_print_page` chooses `k1`, `k4`, or `r8g8b8` channel strings from inferred `ldepth`, reads rendered Ghostscript scan lines, repacks grayscale depths when needed, and sends each line to the compressed Plan 9 image writer.
- The local `WImage` compressor keeps a sliding 1024-byte input window, hash chains, raw dump runs, and compressed match records, flushing fixed-size compressed blocks to the output stream.
- `bytesperline`, `wordsperline`, and `unitsperline` are copied Plan 9/Brazil drawing-library helpers for scanline sizing.

Notable dependencies:
- Ghostscript printer and parameter APIs: `gdevprn.h`, `gsparam.h`.
- Color/luminance and stdio wrappers: `gxlum.h`, `gxstdio.h`.
- External Plan 9 color support from `init_p9color()` in `gdevifno.c`.

Research notes:
- This is output-format code in the in-scope 9front Ghostscript tree, not filesystem logic.
- The device infers output depth from color-map calls; if `print_page` is called again without new color mapping, it reuses `lastldepth`.
- `ldepth == 1` currently returns a fatal error even though 2-bit-per-pixel metadata arrays exist.
- `initwriteimage` allocates compressor state with plain `malloc`, while `plan9_print_page` uses Ghostscript allocation for the scanline buffer; cleanup is split between `writeimageblock(..., nil, 0)` and direct Ghostscript frees.
- Error paths after `initwriteimage` failure do not free the scanline buffer before returning fatal.
