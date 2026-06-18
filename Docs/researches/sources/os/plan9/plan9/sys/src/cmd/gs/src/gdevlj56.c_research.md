# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevlj56.c

Implements Ghostscript devices for HP LaserJet 5/6 PCL XL output: `lj5mono` and `lj5gray`. The mono device is 1-bit; the gray device is 8-bit grayscale with default gray mapping procedures.

The device writes a PCL XL file header in `ljet5_open`, a trailer in `ljet5_close`, and page/image records in `ljet5_print_page`. It relies on PCL XL helper headers (`gdevpx*`) plus stream output wrappers.

`ljet5_print_page` writes page setup, media selection, color space setup, image attributes, then emits every scanline with `eRLECompression`. Compression uses `gdev_pcl_mode2compress_padded`.

The implementation allocates a word-aligned scanline buffer and a worst-case compressed output buffer. It writes every raster line rather than doing sparse image segmentation, despite defining `MIN_SKIP_LINES`.

Main dependencies are Ghostscript printer memory access, PCL XL attribute/opcode helpers, and stream buffering. Failures are mostly allocation or scanline-copy errors.
