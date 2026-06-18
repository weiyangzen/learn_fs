# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/rgb524mn.c

Generic IBM RGB52x-compatible RAMDAC controller using externally supplied indexed register access functions. It computes M/N/divider PLL settings and programs pixel-format, sync, and clock registers for 8/15/16/32 bpp modes.

Key behavior:
- Exports global function pointers `rgb524mnxi` and `rgb524mnxo`; another chip-specific controller must install these to read/write DAC registers.
- Defines RGB52x index registers for misc clock, sync control, pixel controls, PLL controls, SYSCLK, M/N clock pairs, and misc controls.
- `clock` brute-forces divider, M, and N values against the reference clock and max pixel clock, choosing the closest output frequency while respecting VCO/reference constraints.
- `init` parses speed grade from the controller name, uses `rgb524mnrefclk` or default `RefFreq`, validates requested pixel clock, computes PLL values, and selects M/N pair 2.
- `load` verifies callbacks exist, writes selected M/N registers and PLL controls, enables pixel programming and internal PLL clock, sets sync polarity, chooses hsync delay by mode depth or `hsyncdelay` attribute, programs SYSCLK constants, and writes pixel-format/pixel-control registers by depth.
- `dump` reads register ranges and decodes SYSCLK and active pixel PLL frequency.

Notable dependencies:
- External DAC access callbacks must be provided before `load`/`dump`.
- Uses VGA mode and attribute metadata from `vga.h`.

Research notes:
- There is a likely bug in the 15-bpp switch case: after setting `Pixel16Control` to `0xC4`, it falls through into the 16-bpp case and overwrites it with `0xC6`.
- The hard-coded SYSCLK writes and sleeps are visible in `load`, including commented-out alternate values, indicating empirically tuned hardware setup.
- The comment says palette setup needs work for modes other than 8 bits.
