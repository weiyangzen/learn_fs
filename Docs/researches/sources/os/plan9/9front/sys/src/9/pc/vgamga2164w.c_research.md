# File Research: sources/os/plan9/9front/sys/src/9/pc/vgamga2164w.c

## Role

VGA support module for Matrox MGA 2064/2164-class adapters, with framebuffer aperture setup and TVP3026 RAMDAC hardware cursor support.

## Main Interfaces

- Exports `VGAdev vgamga2164wdev` named `mga2164w`.
- Exports `VGAcur vgamga2164wcur` named `mga2164whwgc`.
- Main routines: `mga2164wenable`, `tvp3026enable`, `tvp3026disable`, `tvp3026load`, and `tvp3026move`.

## Key Behavior

- Validates Matrox PCI vendor, distinguishes MGA2064 from later devices, and maps the appropriate framebuffer BAR with `vgalinearaddr`.
- Uses TVP3026 DAC cursor registers for cursor enable, disable, load, and move.
- Loads a 64x64 cursor image into the RAMDAC cursor RAM and programs cursor colors/hotspot bias.
- Handles cursor positioning with negative-coordinate correction.

## Dependencies And Assumptions

- Depends on Matrox PCI device IDs and TVP3026 RAMDAC indexed register behavior.
- Assumes either an 8 MiB or 16 MiB framebuffer aperture depending on device class.

## Research Notes

- The file is a predecessor to the richer MGA4xx module; it does not install acceleration hooks.
