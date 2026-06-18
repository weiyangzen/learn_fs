# File Research: sources/os/plan9/9front/sys/src/9/pc/vgargb524.c

## Role

Hardware cursor support for IBM RGB524-compatible RAMDACs.

## Main Interfaces

- Exports `VGAcur vgargb524cur` named `rgb524hwgc`.
- Main routines: `rgb524enable`, `rgb524disable`, `rgb524load`, `rgb524move`, and indexed DAC helpers.

## Key Behavior

- Selects RAMDAC register banks and indexed cursor registers through RS2/index/data access.
- Programs cursor mode, cursor control, color registers, and cursor hotpoint bias.
- Loads the Plan 9 cursor into the RGB524 64x64 cursor RAM layout.
- Moves the cursor by writing indexed X/Y position registers with offscreen/hotspot correction.

## Dependencies And Assumptions

- Depends on IBM RGB524 RAMDAC register semantics and VGA DAC I/O helpers.
- Exports only a cursor driver, intended to be combined with a separate chipset `VGAdev`.

## Research Notes

- Like `vgabt485.c`, this file is RAMDAC-specific rather than PCI adapter-specific.
