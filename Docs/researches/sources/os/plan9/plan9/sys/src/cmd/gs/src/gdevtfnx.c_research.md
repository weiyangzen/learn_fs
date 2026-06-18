# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevtfnx.c

Implements uncompressed RGB TIFF printer devices `tiff12nc` and `tiff24nc`.

Key behavior:
- Defines a printer-backed TIFF device carrying `gdev_tiff_state`.
- Registers `tiff12nc` and `tiff24nc` as 24-bit Ghostscript RGB devices using the default RGB color mapping procedures.
- Builds a sorted RGB TIFF directory with indirect `BitsPerSample`, no compression, RGB photometric interpretation, MSB fill order, and three samples per pixel.
- Provides separate indirect bits-per-sample values for 4/4/4 RGB (`tiff12nc`) and 8/8/8 RGB (`tiff24nc`).
- `tiff12_print_page` fetches 24-bit rows, packs high nibbles from six source bytes into three 12-bit RGB output bytes, and writes `(width * 3 + 1) >> 1` bytes per row.
- `tiff24_print_page` writes fetched printer rows directly as 24-bit RGB data.
- Both print paths open the TIFF page directory, write all rows as one strip, patch strip metadata, finalize the page, and free the row buffer.

Dependencies:
- Uses `gdevprn.h`, `gdevtifs.h`, Ghostscript printer raster access, and the shared TIFF page writer.

Research notes:
- The 12-bit device still renders internally through a 24-bit printer device and reduces precision only at file output.
- Error handling returns early on allocation or row fetch failure, but the allocated row buffer is only freed along the normal block path after allocation.
