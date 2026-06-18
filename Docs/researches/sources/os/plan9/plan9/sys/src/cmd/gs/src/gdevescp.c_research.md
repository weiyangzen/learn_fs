# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevescp.c

Epson ESC/P2 raster printer driver for `st800` and `ap3250`.

Key behavior:
- Supports 180/360 DPI combinations.
- Initializes ESC/P2 graphics mode, sets line spacing, handles A4 page commands when compiled.
- Clips to margins on byte boundaries.
- Skips vertical blank bands.
- Compresses each scanline using ESC/P2 run-length coding and emits raster graphics commands.

Risks / notes:
- Resolution validation occurs at print time.
- Compression writes into a fixed work buffer sized to one band; logic assumes worst-case output fits.
