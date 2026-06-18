# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevsj48.c

Purpose: Ghostscript printer driver for the StarJet SJ48 printer.

Key behavior:
- Defines `sj48`, an 8x10.5 inch monochrome printer device defaulting to 360x360 dpi.
- Supports only 180/360 dpi combinations in each axis and chooses SJ48 graphics modes 39, 40, 71, or 72.
- Allocates input scanline and transposed output buffers.
- Skips blank scanlines vertically using `ESC J`.
- Converts scanlines into vertical column graphics blocks using `gdev_prn_transpose_8x8`.
- Skips blank horizontal column groups with `ESC \`.
- Emits graphics blocks with `ESC *`, carriage returns after passes, and form feed at page end.

Important dependencies:
- Ghostscript printer helpers: raster sizing, scanline copying, 8x8 transpose.

Notable risks / findings:
- Strictly printer-protocol code; no local filesystem logic.
- Error path flushes/ejects via form feed once output has begun.
