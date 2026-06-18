# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevescp.c

## Role
`gdevescp.c` implements Epson ESC/P2 raster graphics printer devices for `st800` and `ap3250`.

## Device Definitions
- Provides default 360x360 DPI, with valid runtime combinations limited to 180x180, 360x180, or 360x360.
- Defines separate margin constants for Stylus 800 and AP3250.
- Both devices use `escp2_print_page`.

## Print Path
- Allocates two band buffers for 24-scanline bands.
- Resets the printer, enters graphics mode, optionally sends A4 paper/margin commands, and configures line spacing based on vertical resolution.
- Calculates printable top/bottom and byte-aligned left/width limits.
- Skips blank vertical regions with ESC/P2 vertical move commands.
- Compresses each scanline using a PackBits-like scheme: literal runs are length-prefixed, repeated-byte runs use negative/count encoding, and long runs are split at 128 bytes.
- Emits ESC/P2 raster graphics command `ESC .` with resolution, band height, width, compressed data, and CR/LF, then form-feeds and resets.

## Risks and Notes
- Explicitly returns rangecheck for unsupported resolution combinations and VMerror for buffer allocation failures.
- No horizontal whitespace skip; compression is expected to reduce blank-line cost.
- Filesystem relevance is limited to writing printer command bytes to the Ghostscript output stream.
