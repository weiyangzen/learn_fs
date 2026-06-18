# File Research: sources/os/plan9/9front/sys/src/9/pc/vganeomagic.c

## Role

VGA support module for NeoMagic laptop graphics adapters, including PCI device matching, cursor MMIO setup, framebuffer mapping, and 2D fill/scroll acceleration.

## Main Interfaces

- Exports `VGAdev vganeomagicdev` named `neomagic`.
- Exports `VGAcur vganeomagiccur` named `neomagichwgc`.
- Main routines: `neomagicenable`, `neomagicdrawinit`, `neomagiccurenable`, `neomagiccurdisable`, `neomagiccurload`, `neomagiccurmove`, `neomagichwfill`, and `neomagichwscroll`.

## Key Behavior

- Validates NeoMagic PCI vendor `0x10C8`, switches on supported device IDs, determines MMIO BAR, cursor-register offset, and video memory size.
- Uses the top of video memory for two cursor images and maps the PCI framebuffer through `vgalinearpci()`.
- Represents cursor registers with `CursorNM`, writes cursor color, address, enable, and position fields, and handles offscreen cursor adjustment.
- Defines NeoMagic blitter registers and flags, waits for FIFO/idle, and accelerates solid fills and screen-to-screen scrolls.
- `neomagicdrawinit()` maps MMIO/register space and installs fill/scroll callbacks for supported modes.

## Dependencies And Assumptions

- Depends on NeoMagic device-specific BAR and cursor offset choices.
- Acceleration assumes MMIO registers are mapped and the selected depth is supported by the blitter path.

## Research Notes

- The file reserves two cursor images so partial offscreen cursor moves can rewrite a shifted cursor without corrupting the normal image.
