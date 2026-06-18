# File Research: sources/os/plan9/9front/sys/src/9/pc/vgacyber938x.c

## Role

VGA support module for Trident Cyber938x adapters, providing bank switching, PCI linear aperture setup, and hardware cursor support.

## Main Interfaces

- Exports `VGAdev vgacyber938xdev` named `cyber938x`.
- Exports `VGAcur vgacyber938xcur` named `cyber938xhwgc`.
- Main routines: `cyber938xpage`, `cyber938xlinear`, `cyber938xcurenable`, `cyber938xcurdisable`, `cyber938xcurload`, and `cyber938xcurmove`.

## Key Behavior

- Switches framebuffer banks through Trident extended registers.
- Uses `vgalinearpci()` to configure linear memory.
- Loads the Plan 9 cursor into a 64x64 hardware cursor area in display memory.
- Programs cursor address, X/Y position, colors, and enable bits using Cyber938x CRT registers.

## Dependencies And Assumptions

- Depends on Trident-specific extended VGA register semantics.
- Assumes cursor storage has been reserved in display memory via `scr->storage`.

## Research Notes

- The exported `VGAdev` has no enable/disable/drawinit hooks; it supplies page and linear-aperture functions.
