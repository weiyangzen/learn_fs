# File Research: sources/os/plan9/9front/sys/src/9/pc/vgahiqvideo.c

## Role

VGA support module for Chips & Technologies HiQVideo adapters, including PCI validation, linear aperture setup, and hardware cursor support.

## Main Interfaces

- Exports `VGAdev vgahiqvideodev` named `hiqvideo`.
- Exports `VGAcur vgahiqvideocur` named `hiqvideohwgc`.
- Main routines: `hiqvideoenable`, `hiqvideolinear`, `hiqvideocurenable`, `hiqvideocurdisable`, `hiqvideocurload`, and `hiqvideocurmove`.

## Key Behavior

- Validates PCI vendor `0x102C`, selects device-specific behavior, and configures extended registers for display memory size and aperture mode.
- Uses `vgalinearpci()` and publishes a `hiqvideoscreen` segment for the mapped framebuffer.
- Programs cursor memory address, cursor mode, colors, and X/Y position through extended index/data registers.
- Converts the Plan 9 cursor into the adapter’s cursor bitmap layout and stores it in display memory.

## Dependencies And Assumptions

- Depends on HiQVideo extended register ports (`Xrx`) and PCI BAR state.
- Assumes display memory size can be derived from adapter register bits and that cursor storage is in framebuffer memory.

## Research Notes

- No drawing acceleration hook is installed; the module handles setup and cursor functions.
