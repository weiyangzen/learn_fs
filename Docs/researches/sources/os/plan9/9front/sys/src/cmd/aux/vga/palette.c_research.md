# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/palette.c

Generic VGA DAC palette controller for Plan 9 `aux/vga`. It reads, initializes, loads, and dumps the 256-entry VGA palette and pixel mask.

Key behavior:
- `xnto32` expands an `n`-bit color component into a 32-bit repeated pattern for scaling.
- `setcolour` stores high 6-bit red/green/blue values into a DAC palette entry.
- `snarf` reads the current pixel mask, status, and all `Pcolours` DAC entries through VGA palette ports.
- `init` clears the palette, sets pixel mask to `0xFF`, and builds either an 8-bit indexed color cube with special gray entries or a 16-entry grayscale ramp for other depths.
- `load` writes the pixel mask and all DAC entries back to hardware.
- `dump` prints palette values in compact rows.

Notable dependencies:
- VGA port helpers `vgai`/`vgao`, palette constants `Pcolours`, `PaddrR`, `PaddrW`, `Pdata`, `Pixmask`, and color indexes from `vga.h`.

Research notes:
- Palette indexes are XORed with `0xFF` during initialization, matching Plan 9’s expected color map ordering.
- DAC values are 6-bit components even though inputs are represented through 32-bit expansion helpers.
