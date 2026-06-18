# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/onechan.c

## Purpose
Converts arbitrary Plan 9 images to one byte per pixel, usually CMAP8/RGBV, for GIF writing.

## Behavior
Leaves GREY1/2/4, CMAP8, and GREY8 unchanged. For easy RGB formats, unloads pixels directly; for other formats, first draws to RGB24. It repacks RGB16/RGB24/RGBA32/ARGB32 into a temporary `Rawimage`, passes it through `torgbv`, and loads the resulting CMAP8 bytes into a new image.

## APIs
Exports `onechan(Image*)` and `memonechan(Memimage*)`.
