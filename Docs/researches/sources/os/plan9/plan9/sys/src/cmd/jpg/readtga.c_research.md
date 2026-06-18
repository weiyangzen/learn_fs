# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/readtga.c

## Purpose
TGA decoder for image viewer front ends.

## Format Support
Reads 18-byte TGA headers, optional color maps, uncompressed RGB, uncompressed greyscale, RLE RGB, and RLE greyscale. Supports 16/24/32-bit RGB input and ignores alpha channels.

## Implementation
Decodes BGR(A) input into separate R/G/B channel buffers or luma into one channel. Applies vertical flip for lower-left origin and horizontal reflection when x origin indicates right-origin storage.

## Limits
Color-mapped and more exotic compressed TGA types are rejected.
