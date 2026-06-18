# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/cmap.c

Generated default `Memcmap` table.

Key content:
- Static `Memcmap def` containing:
  - `cmap2rgb[3*256]`: CMAP8 index to RGB triples.
  - `rgb2cmap[16*16*16]`: 4-bit-per-channel RGB cube to nearest CMAP8 index.
- `memdefcmap`: global pointer to the default table.
- `_memmkcmap`: no-op because the table is pre-generated.

Used by color-mapped image conversion in `draw.c` and allocation/channel setup.
