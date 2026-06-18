# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/writeppm.c

## Purpose
ASCII Netpbm writer for `Image` and `Memimage`.

## API Surface
Exports `writeppm` and `memwriteppm`.

## Format Handling
Writes P1 for GREY1, P2 for GREY2/GREY4/GREY8, and P3 for RGB24. Optional comments are emitted after the magic. Pixel data is unloaded from draw/memdraw images and printed with line wrapping around 70 columns.

## Limits
Does not write raw P4/P5/P6; unsupported channel types return errors.
