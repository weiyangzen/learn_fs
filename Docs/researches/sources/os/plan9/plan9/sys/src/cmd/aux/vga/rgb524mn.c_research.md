# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/rgb524mn.c

Generic IBM RGB52x/RGB524-compatible RAMDAC module using caller-supplied indexed-register access callbacks.

Key behavior:
- Exports global function pointers `rgb524mnxi` and `rgb524mnxo`; board code such as `t2r4.c` installs accessors.
- Brute-force searches divider/select values for the closest pixel clock under reference-clock and max-pixel-clock constraints.
- Uses `rgb524mnrefclk` database attribute or `RefFreq`.
- Programs M/N register pair 2 by default and selects internal PLL frequency.
- Configures SyncControl polarity, HSync delay, SYSCLK registers, palette control, and pixel format/control for 8, 15/16, and 32 bpp modes.
- Dumps register banks plus SYSCLK and selected pixel PLL clocks.

Important details:
- `load()` errors if access callbacks are unset.
- 15 bpp case falls through into 16 bpp setup after writing `0xC4`, likely intentional or unfinished given the comment about non-8-bit work.
- Contains hard-coded SYSCLK programming and sleeps.

Filesystem relevance:
- Indirect hardware-support code.
