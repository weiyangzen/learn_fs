# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/bmp.c

## Purpose
Command-line BMP viewer/converter front end.

## Behavior
Reads BMP images via `readbmp(fd, CRGB)`, converts to display or output format using `torgbv` or `totruecolor`, optionally displays via libdraw/event, and can emit Plan 9 raw image headers/data or compressed rawimage format.

## Options
Supports common image tool flags: `-c` compressed output, `-9` uncompressed Plan 9 output, `-d` no display, `-e` disable error diffusion, `-k` grey, `-v` RGBV/CMAP8, `-t` true color, and `-3` three-color output.

## Dependencies
Uses `imagefile.h`, `readbmp`, `writerawimage`, libdraw, and event keyboard handling.
