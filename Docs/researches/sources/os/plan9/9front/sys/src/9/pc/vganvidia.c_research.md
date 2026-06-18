# File Research: sources/os/plan9/9front/sys/src/9/pc/vganvidia.c

## Role

VGA support module for NVIDIA adapters, including framebuffer/MMIO setup, hardware cursor support, DMA-assisted graphics engine setup, blanking, and 2D fill/scroll acceleration.

## Main Interfaces

- Exports `VGAdev vganvidiadev` named `nvidia`.
- Exports `VGAcur vganvidiacur` named `nvidiahwgc`.
- Main routines: `nvidiaenable`, `nvidialinear`, `nvidiadrawinit`, `nvidiablank`, cursor routines, `nvidiahwfill`, `nvidiahwscroll`, and DMA helpers.

## Key Behavior

- Maps NVIDIA MMIO and framebuffer regions from PCI BARs, records device ID, and publishes named `nvidiammio` and `nvidiascreen` segments.
- Determines video memory size from PCI/configuration state and maps linear framebuffer access.
- Stores hardware cursor data in framebuffer memory, writes cursor position/address/control registers, and handles offscreen cursor positioning.
- Sets up a DMA push buffer/ring for graphics commands, including put/get pointers and kickoff/wait helpers.
- Resets/initializes selected graphics objects and methods, then uses them for accelerated rectangle fill and screen scroll.
- Installs blanking, fill, and scroll callbacks from `nvidiadrawinit()`.

## Dependencies And Assumptions

- Depends on NVIDIA-specific MMIO, PFIFO/PGRAPH/DMA register behavior and PCI BAR layout.
- Several helper routines are exported without `static`, suggesting coupling with local debugging or related driver code.
- DMA initialization can fail if the push buffer cannot be mapped.

## Research Notes

- The file carries an NVIDIA license header and contains more vendor-specific engine setup than most legacy VGA modules.
