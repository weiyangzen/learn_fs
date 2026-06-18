# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/rgbycc.c

## Purpose
Generator for YCbCr lookup tables.

## Behavior
Computes `ycbcrmap[256]`, mapping Plan 9 colormap entries into Y/Cb/Cr, and `closestycbcr[4096]`, mapping 4-bit YCbCr cube cells to closest colormap indices.

## Notes
Uses 601-style floating-point conversion constants and edge-case constraints for high luma/chroma values. Output is C source table text for a generated header.
