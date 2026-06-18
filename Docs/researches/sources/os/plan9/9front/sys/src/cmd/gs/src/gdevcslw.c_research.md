# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcslw.c

Ghostscript CoStar LabelWriter II/II Plus driver.

Key behavior:
- Defines two monochrome printer devices:
  - `coslw2p` at 128 DPI.
  - `coslwxl` at 204 DPI.
- `coslw_print_page` allocates word-aligned scanline storage, clears temporary storage, scans rendered rows, masks bits beyond page width, skips blank rows with `ESC f` spacing commands, caps output width at 56 bytes for the 2-inch model, changes bytes-per-line with `ESC D`, writes raster lines with `0x16`, and ejects with `ESC E`.

Notable dependencies:
- Ghostscript printer APIs.

Research notes:
- Compression is explicitly left as a possible future improvement.
- The driver is simple monochrome raster output with printer command framing and blank-line optimization.
