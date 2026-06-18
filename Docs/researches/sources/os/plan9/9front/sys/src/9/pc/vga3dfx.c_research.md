# File Research: sources/os/plan9/9front/sys/src/9/pc/vga3dfx.c

## Role

VGA support module for 3dfx graphics adapters, focused on linear framebuffer setup and hardware cursor support.

## Main Interfaces

- Exports `VGAdev vga3dfxdev` named `3dfx`.
- Exports `VGAcur vga3dfxcur` named `3dfxhwgc`.
- Main routines: `tdfxenable`, `tdfxcurenable`, `tdfxcurdisable`, `tdfxcurload`, and `tdfxcurmove`.

## Key Behavior

- Validates PCI vendor `0x121A` and requires a memory BAR, then maps the linear framebuffer with `vgalinearpci`.
- Treats cursor registers as a small `Cursor3dfx` structure in MMIO.
- Loads the Plan 9 16x16 cursor into the adapter’s larger cursor bitmap format, tracks hotspot offsets, and handles negative/offscreen cursor positions by adjusting origin and offsets.
- Enables/disables cursor display through `vidProcCfg` bits and sets cursor colors/registers during enable.

## Dependencies And Assumptions

- Depends on PCI discovery already stored in `scr->pci`, `screen.h` VGA structures, and Plan 9 cursor bitmaps.
- Assumes the 3dfx cursor register layout and framebuffer mapping match the expected adapter generation.

## Research Notes

- No acceleration hooks are installed; this module only supplies device enable and hardware cursor operations.
