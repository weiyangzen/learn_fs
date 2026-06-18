# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/ppm.c

## Purpose
PBM/PGM/PPM viewer/converter front end.

## Behavior
Reads Netpbm images through `readpixmap`, converts with `torgbv` or `totruecolor`, optionally displays, and emits Plan 9 uncompressed or compressed rawimage data.

## Options
Uses the common image flags `-39cdektv`.

## Dependencies
Uses `readpixmap`, conversion helpers, `writerawimage`, libdraw, Bio, and event handling.
