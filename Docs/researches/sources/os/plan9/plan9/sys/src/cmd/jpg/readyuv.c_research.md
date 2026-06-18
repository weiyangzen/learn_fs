# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/readyuv.c

## Purpose
Decoder for Abekas A66-style raw YUV image files.

## Behavior
Infers dimensions and 8/10-bit storage from `/lib/video.specs` and file size. Reads base 8-bit interleaved 4:2:2 samples and, for 10-bit files, reads separate low-bit packing to reconstruct 10-bit samples.

## Color Conversion
Converts Cb/Y/Cr/Y pairs to RGB using fixed-point 601/HD coefficients and clips to 8-bit output.

## Output
Returns one three-channel `Rawimage`, descriptor `CRGB`.
