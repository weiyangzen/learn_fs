# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/readgif.c

## Purpose
GIF decoder returning an array of `Rawimage` frames.

## Format Support
Recognizes GIF87a/GIF89a, global and local color maps, Graphic Control Extension, comments/application/plain-text extension skipping, Netscape loop-count extension, image descriptors, LZW image data, and interlacing.

## Implementation
Uses a `Header` state with `setjmp`/`longjmp` error unwinding. `decode()` implements GIF LZW with clear/EOD codes, dynamic table entries, KwKwK handling, sub-block reading, and optional clipping of invalid palette indices.

## Output
Each frame is `CRGB1` indexed data with colormap, rectangle, GIF flags, delay, transparent index, and loop count.
