# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcslw.c

Ghostscript driver for CoStar LabelWriter II/II Plus style label printers.

Key responsibilities:
- Defines `coslw2p` and `coslwxl` monochrome devices.
- Copies rendered monochrome scanlines, trims trailing zero words, and skips blank lines.
- Emits LabelWriter spacing, line-width, raster data, and eject commands.
- Caps output line width to 56 bytes for the 2-inch model.

Important behavior:
- `coslw2p` is 2 inches wide at 128 dpi; `coslwxl` uses 204 dpi.
- Blank lines are emitted through repeated `ESC f 1 <count>` spacing commands, chunked at 255 lines.
- If the byte width changes, the driver emits `ESC D <out_count>`.
- Raster data is introduced with `0x16`, followed by raw row bytes.
- Page eject uses `ESC E`.

Dependencies:
- Ghostscript printer API from `gdevprn.h`.

Notable risks:
- No compression is implemented; comment says it may be added later.
- The driver keeps zero initialization and unused storage beyond the active scanline, but only uses the first line-sized region.
- Width is hard-capped to 56 bytes regardless of the higher-resolution model's potential geometry.
