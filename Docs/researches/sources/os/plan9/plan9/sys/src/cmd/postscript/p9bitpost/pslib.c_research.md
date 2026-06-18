# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/p9bitpost/pslib.c

PostScript image output library for Plan 9 `Memimage` objects.

Key responsibilities:
- Emits DSC headers, a PostScript image prologue, page wrapper, image data, and trailer.
- Supports indexed Plan 9 colormap, grayscale, and 24-bit RGB image output.
- Converts image data to ASCII85.
- Removes line padding and aligns sub-byte images to byte boundaries.
- Computes fit-to-page dimensions for portrait or landscape output.
- Supports x/y magnification, landscape mode, and raw PostScript patch injection.

Important behavior:
- For non-CMAP/GREY images with depth >= 8, converts to `b8g8r8`.
- Image bytes are inverted (`255 - src`) before encoding.
- ASCII85 zero groups are compressed as `z`, except partial final groups.
- If DPI is supplied, output size is based on pixel dimensions and DPI; otherwise it fits within 0.5-inch margins.

Dependencies:
- Uses Plan 9 `Memimage`, `Biobuf`, `bytesperline`, `byteaddr`, `memimagedraw`, and `allocmemimage`.

Notable risks:
- Large PostScript colormap is embedded for every output file.
- Commented-out Inferno/Tk text code remains in the file but is inactive.
- `imagebits()` allocates a compacted full image buffer in memory.
