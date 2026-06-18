# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/g3p9bit/g3p9bit.c

Group 3 fax decoder to Plan 9 bitmap format.

Key responsibilities:
- Reads Group 3 modified Huffman fax data from several container/header variants.
- Builds white and black code lookup tables from included `wtab` and `btab`.
- Decodes fax rows into a 1728-pixel-wide bitmap.
- Writes a Plan 9 bitmap header and raster bytes.
- Supports simulated 2-bit gray horizontal compression (`-g`) and scanline doubling (`-y`).

Important behavior:
- Recognizes a PC/TIFF-like `II*` offset, a “PC Research, Inc” digifax format, and text headers with `FDCS=`.
- Only supports width code 0 and 1-D modified Huffman compression.
- High vertical resolution halves output row count after decoding.
- `sync()` skips to the next EOL code.

Dependencies:
- Includes generated Huffman tables `btab` and `wtab`.

Notable risks:
- Reads the entire input into a fixed 1 MiB buffer.
- Uses fixed maximum page dimensions: 1728 dots and 1410 lines.
- Error handling may emit a valid-looking partial bitmap before reporting a trailing decode error.
