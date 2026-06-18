# File Research: sources/os/plan9/9front/sys/src/9/pc/vgaclgd546x.c

## Role

VGA support module for Cirrus Logic GD546x adapters, with PCI linear framebuffer setup and MMIO-style hardware cursor support.

## Main Interfaces

- Exports `VGAdev vgaclgd546xdev` named `clgd546x`.
- Exports `VGAcur vgaclgd546xcur` named `clgd546xhwgc`.
- Main routines: `clgd546xenable`, `clgd546xlinear`, `clgd546xcurenable`, `clgd546xcurdisable`, `clgd546xcurload`, and `clgd546xcurmove`.

## Key Behavior

- Uses `vgalinearpci()` for linear framebuffer mapping.
- Maps cursor control through a `Cursor546x` register structure.
- Stores a 64x64 cursor bitmap in display memory, converts Plan 9 cursor mask/set data into the adapter format, and tracks hotspot offsets.
- Enables/disables and moves the hardware cursor by writing cursor control, address, color, and X/Y registers.

## Dependencies And Assumptions

- Depends on PCI-backed VGA screen state and a known GD546x cursor register block.
- Requires `scr->storage` to point to display memory reserved for cursor data.

## Research Notes

- No drawing acceleration hooks are exported; this module is cursor and aperture setup only.
