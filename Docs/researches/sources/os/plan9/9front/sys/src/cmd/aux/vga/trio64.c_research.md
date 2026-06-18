# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/trio64.c

Implements support for S3 Trio64 controllers and the Trio64 pixel clock PLL.

Key responsibilities:
- Unlocks and snarfs extended Trio sequencer and CRT registers.
- Advertises linear, enhanced, and 2x8 pixel clock capabilities.
- Implements `trio64clock`, the shared S3 PLL search used by Trio64 and ViRGE-family drivers.
- Programs VGA standard clock selection or DCLK PLL registers depending on requested frequency.
- Handles internal clock generator setup and optional 2x8 mode.
- Programs S3 advanced function register `0x4AE8` for enhanced mode.

Important interfaces:
- Exports `Ctlr trio64` and `void trio64clock(Vga*, Ctlr*)`.
- Relies on `s3generic` for base S3 register handling.
- Uses PLL fields in `Vga`: `f`, `m`, `n`, `r`, and `d`.

Notes:
- Rejects depths above 8 bpp in this Trio64 implementation.
- `trio64clock` searches M/N/R values and enforces roughly 0.5% output error.
- `dump` reconstructs and prints DCLK from saved PLL registers.
