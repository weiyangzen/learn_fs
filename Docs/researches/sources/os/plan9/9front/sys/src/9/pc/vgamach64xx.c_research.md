# File Research: sources/os/plan9/9front/sys/src/9/pc/vgamach64xx.c

## Role

VGA support module for ATI Mach64-family adapters, including PCI adapter identification, linear aperture setup, hardware cursor, display blanking, LCD blanking, and optional 2D fill/scroll acceleration.

## Main Interfaces

- Exports `VGAdev vgamach64xxdev` named `mach64xx`.
- Exports `VGAcur vgamach64xxcur` named `mach64xxhwgc`.
- Main routines: `mach64xxenable`, `mach64xxlinear`, `mach64xxdrawinit`, `mach64blank`, `mach64lcdblank`, cursor routines, `mach64hwfill`, and `mach64hwscroll`.

## Key Behavior

- Validates ATI PCI vendor `0x1002`, matches a table of Mach64 device IDs/types, records revision capability, and maps PCI linear framebuffer with `vgalinearpci()`.
- Defines extensive Mach64 register constants and helpers for MMIO/IO register access plus LCD register access.
- Hardware cursor logic stores cursor image data in display memory, programs cursor offset/color/position, and handles partial offscreen movement.
- Initializes the 2D engine by resetting it, setting pitch/offset, data path, scissor, pixel depth, and default mix/ROP state.
- `mach64hwfill()` accelerates solid rectangle fills; `mach64hwscroll()` accelerates screen-to-screen rectangle copies with direction handling.
- Installs acceleration hooks only for supported formats/depths and sets blanking hooks for CRT/LCD variants.

## Dependencies And Assumptions

- Depends on ATI Mach64 PCI IDs, MMIO register layout, and Plan 9 `VGAscr` acceleration callbacks.
- Rejects unsupported pixel formats through the shared `Eunsupportedformat` error string.
- FIFO/idle wait loops assume hardware eventually drains; timeouts are limited but still hardware-sensitive.

## Research Notes

- This is one of the richer VGA files in the group because it includes both cursor and 2D acceleration.
- LCD blanking support is separate from CRT blanking and uses Mach64 LCD-indexed registers.
