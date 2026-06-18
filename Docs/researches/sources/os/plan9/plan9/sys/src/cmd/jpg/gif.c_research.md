# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/gif.c

## Purpose
GIF viewer/converter front end with animation and transparency support.

## Behavior
Reads one or more GIF frames using `readgif`, converts each frame to CMAP8, grey, RGB24, or alpha-bearing output, displays animation using frame delays and loop count, and writes only the first frame for raw/Plan 9 output.

## GIF-Specific Handling
Creates masks for transparent-index GIF frames. When writing output for transparent GIFs, `addalpha()` expands CMAP/Grey/RGB data to include alpha, and `blackout()` zeros transparent pixels.

## Options
Uses the common `-39cdektv` image flags. Display mode supports frame looping and exits on `q`, delete, or EOF control character.

## Dependencies
Uses `readgif`, `torgbv`, `totruecolor`, `writerawimage`, libdraw, and event handling.
