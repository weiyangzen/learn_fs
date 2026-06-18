# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/close.c

## Purpose
Utility generator for YCbCr-to-RGBV lookup data.

## Behavior
Computes the closest Plan 9 colormap index for YCbCr values by converting to RGB and minimizing squared RGB distance across all 256 Plan 9 colormap entries. It buckets the 24-bit Y/Cb/Cr cube into `32^3` cells and records which colormap indices occur in each cell.

## Notes
This is a table-generation/support program, not a normal image conversion command. It is CPU-heavy by design, iterating all 256^3 YCbCr triples.
