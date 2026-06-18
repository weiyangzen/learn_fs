# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/rgbv.h

## Purpose
Generated lookup table header for Plan 9 RGBV/CMAP8 conversion.

## Contents
Defines `rgbmap[256]`, mapping each Plan 9 colormap index to packed RGB, and `closestrgb[4096]`, mapping 4-bit RGB cube cells to closest colormap indices.

## Usage
Consumed by `torgbv.c` for fast truecolor-to-CMAP8 conversion and error diffusion.
