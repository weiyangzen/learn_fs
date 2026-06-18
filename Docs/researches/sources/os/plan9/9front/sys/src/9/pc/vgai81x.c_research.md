# File Research: sources/os/plan9/9front/sys/src/9/pc/vgai81x.c

## Role

VGA support module for Intel i81x integrated graphics, focused on aperture sizing, display blanking, and hardware cursor support.

## Main Interfaces

- Exports `VGAdev vgai81xdev` named `i81x`.
- Exports `VGAcur vgai81xcur` named `i81xhwgc`.
- Main routines: `i81xenable`, `i81xblank`, `i81xcurenable`, `i81xcurdisable`, `i81xcurload`, and `i81xcurmove`.

## Key Behavior

- Reads PCI configuration and graphics control bits to determine aperture/framebuffer size.
- Maps framebuffer memory with `vgalinearaddr`.
- Implements blanking by toggling display-control register bits.
- Stores the hardware cursor image in display memory and writes cursor position/base/control registers.
- Converts the Plan 9 cursor into the i81x cursor bitmap format and tracks hotspot offsets.

## Dependencies And Assumptions

- Depends on Intel i81x PCI BAR/control layout and MMIO registers mapped through `scr`.
- Assumes cursor storage is available in mapped video memory.

## Research Notes

- The exported `VGAdev` does not provide a linear callback because mapping is performed in `i81xenable`.
