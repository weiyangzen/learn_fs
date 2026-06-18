# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevatx.c

Practical Automation ATX-23, ATX-24, and ATX-38 printer driver.

Key points:
- Defines `atx23`, `atx24`, and `atx38` devices with model-specific page widths, DPI, and margins.
- Encodes ATX printer commands for page length, vertical tab, compressed/uncompressed data, and end page.
- `fput_atx_command` writes a command plus little-endian 16-bit argument.
- `atx_compress` implements pair-oriented run-length compression for repeated byte pairs and uncompressed segments.
- `atx_print_page` computes legal page length, enforces minimum 3-inch page length, allocates scanline/compression buffers, skips blank lines, truncates to maximum printable width, writes compressed or raw scanline data, and ends the page.
- Model wrappers pass maximum pixel widths for the three printers.

Dependencies and interactions:
- Includes `math_.h` and `gdevprn.h`.
- Uses `gdev_prn_get_bits`, Ghostscript allocation helpers, and printer stream writes.

OS/filesystem relevance:
- Streams printer command/raster data through `FILE *`.
