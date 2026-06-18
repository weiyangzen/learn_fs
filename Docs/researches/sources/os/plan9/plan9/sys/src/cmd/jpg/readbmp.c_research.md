# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/readbmp.c

## Purpose
BMP decoder returning `Rawimage` data.

## Format Support
Handles Windows and OS/2 BMP headers, indexed 1/4/8-bit images, 16/24/32-bit truecolor, RLE4, RLE8, top-down and bottom-up images, and 16/32-bit bitfield masks.

## Implementation
Reads little-endian fields through `r16`/`r32`, reads palettes or bit masks, seeks to pixel data, decodes into an intermediate `Rgb` array, then splits into three `Rawimage` channels with descriptor `CRGB`.

## Error Handling
Some malformed inputs call `sysfatal`; allocation cleanup paths return nil. Only `CRGB` output is accepted.
