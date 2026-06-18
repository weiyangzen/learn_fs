# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/readppm.c

## Purpose
Netpbm PBM/PGM/PPM decoder.

## Format Support
Reads P1/P4 bitmap, P2/P5 greymap, and P3/P6 pixmap formats. Handles comments beginning with `#`, decimal integer parsing, ASCII and raw samples, bitmap bit packing, max-value scaling, and PBM inversion.

## Output
Returns a one-element `Rawimage` array. Greyscale formats produce `CY`; pixmap formats produce three-channel `CRGB`.

## Dependencies
Uses Bio and `imagefile.h`.
