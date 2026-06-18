# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/tga.c

## Purpose
TGA viewer/converter front end.

## Behavior
Reads TGA through `readtga`, converts to requested CMAP8/GREY8/RGB24 output, optionally displays through libdraw, and can write Plan 9 uncompressed or compressed rawimage output.

## Options
Uses common image flags `-39cdektv`.

## Dependencies
Uses `readtga`, `torgbv`, `totruecolor`, `writerawimage`, libdraw, and event handling.
