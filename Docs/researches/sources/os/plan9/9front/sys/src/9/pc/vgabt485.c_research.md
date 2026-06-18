# File Research: sources/os/plan9/9front/sys/src/9/pc/vgabt485.c

## Role

Hardware cursor support for Brooktree Bt485-compatible RAMDACs.

## Main Interfaces

- Exports `VGAcur vgabt485cur` named `bt485hwgc`.
- Main routines: indexed DAC register access helpers, `bt485enable`, `bt485disable`, `bt485load`, and `bt485move`.

## Key Behavior

- Implements Bt485 indexed I/O through palette/cursor address and control registers.
- Programs cursor mode 3, external operation mode, and cursor colors.
- Loads a 16x16 Plan 9 cursor into the Bt485 64x64x2 cursor RAM layout, clearing unused rows and columns.
- Maintains hotspot offsets with the DAC’s 64-pixel cursor origin bias and writes X/Y low/high position registers.

## Dependencies And Assumptions

- Depends on VGA DAC I/O helpers and Bt485-compatible register behavior.
- This file exports only a cursor driver, not a full `VGAdev`; it is used by chipset modules that pair with a Bt485 RAMDAC.

## Research Notes

- The implementation is DAC-oriented rather than PCI/chipset-oriented.
- Cursor color handling uses black/white palette entries and does not expose programmable cursor colors.
