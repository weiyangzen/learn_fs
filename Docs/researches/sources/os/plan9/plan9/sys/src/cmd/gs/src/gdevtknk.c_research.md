# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevtknk.c

Implements the `tek4696` printer device for Tektronix 4696/4695 ink-jet plotters.

Key behavior:
- Registers a 4-bit, 120 DPI printer device with a roll-media page size chosen to approximate an A-series aspect ratio.
- Defines a subtractive Tektronix palette using bit planes for black, magenta, yellow, and cyan, with only eight meaningful RGB-derived palette values.
- `tekink_map_rgb_color` thresholds each RGB channel at half intensity and maps the resulting 3-bit RGB code into the printer’s 4-bit ink code.
- `tekink_map_color_rgb` maps valid printer colors back to RGB and rejects unused 4-bit values.
- `tekink_print_page` allocates one input row plus four separated one-bit output planes, one per ink channel.
- For each raster row, separates input 4-bit pixels into black/magenta/yellow/cyan bit planes, trims trailing zero bytes from each plane, and emits Tektronix escape-command line records for nonblank color planes.
- Tracks blank lines for roll-paper devices to skip leading whitespace and compact runs of blank rows into micro-line-feed commands.
- Emits final micro-line-feed/page separation commands and frees the temporary buffer.

Dependencies:
- Uses `gdevprn.h`, `malloc_.h`, Ghostscript printer scan-line copying, and standard C memory/string/file routines.

Research notes:
- The code uses `malloc`/`free` rather than Ghostscript memory allocation.
- It is specific to the Tektronix printer command stream and would need new descriptors/geometric settings for related models.
