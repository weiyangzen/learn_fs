# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/readv210.c

## Purpose
Decoder for single uncompressed QuickTime v210 YUV images.

## Behavior
Infers pixel count, line count, and chunk size from file length using `/lib/video.specs`. Reads packed 10-bit v210 words into 10-bit Y/Cb/Cr samples, then converts 4:2:2 pairs to RGB byte channels.

## Color Conversion
Uses fixed-point coefficients, choosing one coefficient set for 625-line/PAL-like 601 and another for 525-line/HD-style data.

## Output
Returns a three-channel `Rawimage`, descriptor `CRGB`, with dimensions from video specs.
