# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/torgbv.c

## Purpose
Converts `Rawimage` inputs to Plan 9 RGBV/CMAP8 one-byte-per-pixel output.

## Supported Inputs
Handles indexed `CRGB1`, YCbCr, planar RGB, packed RGB24/RGBA32, grey, and grey+alpha. It validates channel counts and color map sizes.

## Conversion
Uses `rgbv.h` and YCbCr lookup tables for nearest-colormap selection. Optional modified Floyd-Steinberg error diffusion spreads per-channel error across rows using 3/16, 3/16, and 7/16-style terms.

## Output
Returns a new `Rawimage` with descriptor `CRGBV` and one channel of CMAP8-compatible bytes.
