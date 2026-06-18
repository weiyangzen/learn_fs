# File Research: sources/os/plan9/9front/sys/src/9/pc/vgaark2000pv.c

## Role

VGA support module for ARK Logic ARK2000PV adapters, including banked framebuffer paging and hardware cursor support.

## Main Interfaces

- Exports `VGAdev vgaark2000pvdev` named `ark2000pv`.
- Exports `VGAcur vgaark2000pvcur` named `ark2000pvhwgc`.
- Main routines: `ark2000pvpage`, `ark2000pvenable`, `ark2000pvdisable`, `ark2000pvload`, and `ark2000pvmove`.

## Key Behavior

- Implements page switching through VGA graphics/controller registers, with separate handling for 8-bit and higher-depth modes.
- Configures cursor memory in the last 16 KiB of video memory and selects cursor storage blocks through extended CRT registers.
- Loads the Plan 9 cursor into the adapter’s 64x64 cursor pattern area, preserving/restoring the bank page when linear addressing is not used.
- Handles cursor motion with hotspot correction and negative-coordinate clipping.

## Dependencies And Assumptions

- Depends on standard VGA register helpers (`vgaxi`, `vgaxo`) and `VGAscr` storage fields.
- Assumes cursor memory is available at the configured high-memory storage offset.

## Research Notes

- This is a legacy banked VGA module; there is no linear aperture setup or drawing acceleration hook in the exported `VGAdev`.
