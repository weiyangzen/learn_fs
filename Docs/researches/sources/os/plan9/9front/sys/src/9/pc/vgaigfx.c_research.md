# File Research: sources/os/plan9/9front/sys/src/9/pc/vgaigfx.c

## Role

VGA support module for newer Intel integrated graphics (`igfx`), providing PCI framebuffer setup, blanking, and hardware cursor support.

## Main Interfaces

- Exports `VGAdev vgaigfxdev` named `igfx`.
- Exports `VGAcur vgaigfxcur` named `igfxhwgc`.
- Main routines: `igfxenable`, `igfxdrawinit`, `igfxblank`, `igfxcurenable`, `igfxcurdisable`, `igfxcurload`, and `igfxcurmove`.

## Key Behavior

- Allocates cursor storage inside the framebuffer, maps the PCI linear aperture with `vgalinearpci()`, and installs `igfxblank` through `drawinit`.
- Selects cursor register blocks by PCI device generation, then writes cursor base, control, and position registers.
- Loads the Plan 9 cursor as ARGB-like 32-bit cursor pixels in framebuffer memory.
- Handles blanking by toggling generation-specific display-plane/control registers.

## Dependencies And Assumptions

- Depends on Intel integrated graphics PCI device IDs and generation-specific cursor/display register offsets.
- Assumes `scr->pci`, `scr->vaddr`, and `scr->storage` are valid after enable.

## Research Notes

- This module is more modern than `vgai81x.c` but still limited to framebuffer/cursor/blanking support, not 2D acceleration.
