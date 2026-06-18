# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevtknk.c

## Purpose
Ghostscript printer driver for Tektronix 4696/4695 inkjet plotters, exposed here as `tek4696`.

## Main Concepts
- Defines a 4-bit subtractive color index model for black, magenta, yellow, cyan, and their simple combinations.
- Maps RGB thresholded colors to Tektronix ink bit combinations.
- Converts Ghostscript raster rows into four 1-bit color planes and emits Tektronix escape-command output.

## Key Functions
- `tekink_map_rgb_color`: threshold maps RGB to one of eight valid ink combinations.
- `tekink_map_color_rgb`: maps valid device indexes back to RGB and rejects unused indexes.
- `tekink_print_page`: allocates a row buffer, splits each scanline into B/M/Y/C bit planes, suppresses trailing blank bytes, emits color-plane commands, handles micro-line feeds, skips leading blank lines on roll paper, and separates plots with feeds or form feed.

## Dependencies
Uses Ghostscript printer APIs and C heap allocation through `malloc_.h`.

## Notable Risks
- Uses raw `malloc`/`free` instead of Ghostscript memory APIs.
- Returns `-1` directly on allocation failure instead of a Ghostscript error code.
- Write errors are not checked.
- File naming/model behavior depends on `pdev->dname` string comparison to detect roll paper.

## Filesystem Relevance
Writes printer command streams only. It is not filesystem implementation code.
