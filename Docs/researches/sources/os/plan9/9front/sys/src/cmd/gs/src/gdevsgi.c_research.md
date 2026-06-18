# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevsgi.c

Ghostscript printer-style output device that writes SGI RGB raster image files.

Key behavior:
- Defines the `sgirgb` 24-bit RGB device at 72 DPI.
- Maps RGB colors into packed color indices based on bits per channel and maps them back to RGB.
- Writes an SGI `IMAGE` header with magic number, 3 dimensions, 3 channels, RLE encoding, dimensions, and image metadata.
- Reserves row-start and row-size tables after the 512-byte header.
- Emits image data as three separated channel planes: red, green, then blue.
- Reads Ghostscript scanlines bottom-up.
- Converts packed pixel data into per-channel bytes.
- Applies SGI-style RLE compression per row and channel.
- Seeks back to fill row-start and row-size tables in big-endian byte order.

Notable dependencies:
- Ghostscript printer API: `gdevprn.h`.
- SGI raster definitions from `gdevsgi.h`.

Research notes:
- The driver is file-format output, not a physical printer despite using printer-device infrastructure.
- Allocation failures return `-1`, not always a Ghostscript-specific error code.
- The code manually writes big-endian table entries.
