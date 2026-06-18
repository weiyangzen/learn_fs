# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/multichan.c

## Purpose
Converts Plan 9 `Image` or `Memimage` values to a simple multi-channel format suitable for PPM writing.

## Behavior
If the image is already GREY1/2/4/8 or RGB24, returns it unchanged. Otherwise allocates an RGB24 image and draws the source into it.

## APIs
Exports `multichan(Image*)` and `memmultichan(Memimage*)`.
