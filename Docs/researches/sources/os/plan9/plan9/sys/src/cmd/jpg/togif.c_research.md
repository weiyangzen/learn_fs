# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/togif.c

## Purpose
Converts Plan 9 image files to GIF.

## Behavior
Reads one or more Plan 9 images as `Memimage`, converts to one-channel CMAP/Grey using `memonechan`, starts a GIF stream, writes frames, and ends the GIF. Supports stdin for a single image.

## Options
`-l` loop count, `-c` comment, `-d` frame delay in milliseconds, and `-t` transparent color index. Multiple input files default to infinite looping; single images default to no loop.

## Dependencies
Uses `memstartgif`, `memwritegif`, `memendgif`, and Plan 9 memdraw image readers.
