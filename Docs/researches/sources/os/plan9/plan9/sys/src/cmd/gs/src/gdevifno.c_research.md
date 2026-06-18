# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevifno.c

Plan 9 / Inferno bitmap output device.

Key behavior:
- Defines `inferno` printer device.
- Tracks requested colors to infer output `ldepth`.
- Converts RGB scanlines to Inferno/Plan 9 colormap formats, including John Hobby dithering table initialization.
- Writes `compressed` Inferno image format with a sliding-window compressor adapted from Plan 9/Brazil drawing tools.
- Supports 1/2/4/8-bit-per-pixel-style depths via `ldepth`, though `ldepth == 1` path is fatal.

Risks / notes:
- Uses both Ghostscript memory and libc `malloc/free`.
- Some parameter get/put code is present but disabled in the active proc table.
- Contains debug `printf` remnants in inactive paths.
