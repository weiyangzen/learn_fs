# File Research: sources/os/plan9/9front/sys/src/9/pc/vgaradeon.c

## Role

VGA support module for ATI Radeon adapters, covering PCI/MMIO setup, hardware cursor support, blanking, optional 2D acceleration, optional overlay hooks, and framebuffer flush.

## Main Interfaces

- Exports `VGAdev vgaradeondev` named `radeon`.
- Exports `VGAcur vgaradeoncur` named `radeonhwgc`.
- Main routines: `radeonenable`, `radeonlinear`, `radeondrawinit`, `radeonblank`, cursor routines, `radeonfill`, `radeonscroll`, `radeonovlctl`, `radeonovlwrite`, and `radeonflush`.

## Key Behavior

- Includes Radeon register definitions from `/sys/src/cmd/aux/vga/radeon.h`.
- Maps Radeon PCI framebuffer/MMIO resources, records device ID, and uses `vgalinearpci()` for linear framebuffer access.
- Provides register helpers for MMIO and PLL indexed access.
- Loads a hardware cursor image in display memory, sets cursor colors, address, enable state, and position.
- Implements blanking by updating CRTC/display control registers.
- When `HW_ACCEL` is enabled at compile time, initializes DP/GUI master control, waits for FIFO/idle, accelerates fills and scrolls, and exposes overlay control/write/flush hooks in `VGAdev`.

## Dependencies And Assumptions

- Depends on ATI Radeon PCI state, MMIO register layout, and the external Radeon header.
- Acceleration and overlay hooks are compile-time gated by `HW_ACCEL`.
- Requires correct cache/flushing behavior for framebuffer writes and overlay updates.

## Research Notes

- This is a compact but broad Radeon module: cursor, blanking, acceleration, overlay, and flush support all live in one file.
