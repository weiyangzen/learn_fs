# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/3dfx.c

VGA controller backend for 3Dfx Banshee, Voodoo3/Avenger, and Voodoo5-class devices.

Core behavior:
- Locates PCI vendor `0x121A`.
- Determines maximum pixel clock by device ID.
- Uses PCI memory BAR 2 as I/O register base.
- Saves 3Dfx MMIO-style registers and VGA CRTC overflow registers.
- Determines video memory size from PCI BAR and DRAM/SGRAM strap registers.
- Supports linear framebuffer and high-clock double-pixel mode above 135 MHz.
- Programs PLL, screen size, stride, pixel format, DAC mode, and overflow registers.

Important functions:
- `snarf()` discovers PCI device and snapshots registers.
- `tdfxclock()` brute-forces PLL `m/n/p`.
- `init()` prepares mode registers and validates depth.
- `load()` writes CRTC and 3Dfx registers.
- `dump()` prints register state and decoded PLL frequencies.

Ctlrs:
- `tdfx`
- `tdfxhwgc` placeholder with no hooks.

Notable risks:
- Direct port I/O through BAR-derived base.
- Supports only selected device IDs.
- Requires x multiple of 16 for high-clock double-pixel mode.
