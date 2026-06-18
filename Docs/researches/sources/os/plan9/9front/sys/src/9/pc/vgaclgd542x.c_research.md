# File Research: sources/os/plan9/9front/sys/src/9/pc/vgaclgd542x.c

## Role

VGA support module for Cirrus Logic GD542x adapters, covering bank switching, optional PCI linear aperture setup, and hardware cursor support.

## Main Interfaces

- Exports `VGAdev vgaclgd542xdev` named `clgd542x`.
- Exports `VGAcur vgaclgd542xcur` named `clgd542xhwgc`.
- Main routines: `clgd542xpage`, `clgd542xlinear`, `clgd542xenable`, `clgd542xdisable`, `clgd542xload`, and `clgd542xmove`.

## Key Behavior

- Switches display banks by updating graphics register `0x09`, using depth-dependent bit placement.
- Uses `vgalinearpci()` for a PCI linear framebuffer when requested.
- Initializes hardware cursor registers, cursor colors, and cursor storage in the last 16 KiB of video memory.
- Loads cursor images through either the linear framebuffer or temporary bank switching, depending on current aperture state.
- Supports two cursor image slots to handle partially offscreen cursor positions.

## Dependencies And Assumptions

- Depends on Cirrus extended VGA registers and standard `VGAscr` fields such as `storage`, `vaddr`, and `apsize`.
- Assumes enough display memory is reserved for cursor storage.

## Research Notes

- The code takes care not to call generic color setters while the cursor lock is held, using direct palette writes instead.
