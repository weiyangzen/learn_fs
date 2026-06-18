# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/palette.c

Implements the generic VGA palette controller for `aux/vga`.

Key behavior:
- `snarf()` reads pixel mask, DAC status, and all 256 RGB palette entries from VGA DAC ports.
- `init()` creates a default palette: color-cube style entries for 8-bit modes and grayscale entries for lower depths.
- `load()` writes the pixel mask and all palette entries back to DAC registers.
- `dump()` prints the complete palette in compact RGB triplets.
- `xnto32()` expands small bitfields to 32-bit intensity, and `setcolour()` converts 32-bit intensities to 6-bit VGA DAC values.

Important details:
- Palette indexes are XORed with `0xFF` when initialized, matching Plan 9’s historic colormap expectations.
- VGA DAC values are 6-bit, even when higher-level color calculations use 32-bit intermediate values.

Filesystem relevance:
- Indirect: part of display mode setup, not filesystem logic.
