# File Research: sources/os/plan9/9front/sys/src/9/pc/vgageode.c

## Role

VGA support module for AMD/NS Geode graphics, covering framebuffer/MMIO setup and hardware cursor support.

## Main Interfaces

- Exports `VGAdev vgageodedev` named `geode`.
- Exports `VGAcur vgageodecur` named `geodehwgc`.
- Main routines: `geodeenable`, `geodelinear`, `geodecurenable`, `geodecurdisable`, `geodecurload`, and `geodecurmove`.

## Key Behavior

- Validates Geode PCI state, maps display/MMIO regions, and adds a named `geodevid` VGA segment for the video memory BAR.
- Uses `vgalinearpci()` for the framebuffer aperture.
- Writes cursor bitmap data and cursor position/control registers through Geode display-controller MMIO.
- Enables and disables the cursor by toggling display-controller cursor-enable bits.

## Dependencies And Assumptions

- Depends on Geode PCI BAR layout, including the video memory BAR used by `addvgaseg`.
- Assumes the MMIO register array is mapped in `scr->mmio`.

## Research Notes

- This module is small and hardware-specific; it has no drawing acceleration hook.
