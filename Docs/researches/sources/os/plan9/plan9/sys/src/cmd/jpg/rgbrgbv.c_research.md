# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/rgbrgbv.c

## Purpose
Generator for RGBV lookup tables.

## Behavior
Computes `rgbmap[256]`, the RGB value of each Plan 9 colormap index, and `closestrgb[16*16*16]`, the closest colormap index for each 4-bit-per-channel RGB cube cell.

## Notes
The file comments that `closest()` is now installed as `rgb2cmap` in libdraw. Output is C source table text intended for inclusion in `rgbv.h`.
