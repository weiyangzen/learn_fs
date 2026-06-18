# File Research: sources/os/plan9/9front/sys/src/9/pc/vgamga4xx.c

## Role

VGA support module for Matrox MGA G200/G400/G450/G550-style adapters, including PCI aperture setup, DAC cursor support, blanking, and 2D fill/scroll acceleration.

## Main Interfaces

- Exports `VGAdev vgamga4xxdev` named `mga4xx`.
- Exports `VGAcur vgamga4xxcur` named `mga4xxhwgc`.
- Main routines: `mga4xxenable`, `mga4xxdrawinit`, `mga4xxblank`, `mga4xxfill`, `mga4xxscroll`, and `dac4xx*` cursor routines.

## Key Behavior

- Uses PCI BAR0 for framebuffer mapping, with larger size for MGA4xx/MGA550 devices.
- Maps MMIO, exposes Matrox register helpers, and programs extended CRTC/DAC cursor registers.
- Loads hardware cursor data into framebuffer memory, sets cursor base address, colors, and X/Y position.
- Implements blanking by manipulating sequencer/CRTC-style control bits.
- Initializes the 2D drawing engine and installs solid fill and screen scroll callbacks.
- `mga4xxfill()` programs drawing registers for rectangle fill; `mga4xxscroll()` performs bitblt copies with direction and pitch handling.

## Dependencies And Assumptions

- Depends on Matrox PCI IDs, BAR layout, MMIO register definitions, and supported framebuffer depths.
- Acceleration setup assumes a linear framebuffer and valid `scr->mmio`.

## Research Notes

- This file is a representative Plan 9 VGA acceleration module: driver setup ultimately installs function pointers into `VGAscr`.
