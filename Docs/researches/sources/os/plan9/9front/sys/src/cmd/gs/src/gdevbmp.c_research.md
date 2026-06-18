# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbmp.c

## Purpose
Implements BMP output devices that render Ghostscript pages into BMP-format files.

## Devices
- `bmpmono`: 1-bit mono
- `bmpgray`: 8-bit grayscale
- `bmpsep1`: separated CMYK, 1 bit per plane
- `bmpsep8`: separated CMYK, 8 bits per plane
- `bmp16`: 4-bit EGA/VGA-style color
- `bmp256`: 8-bit 3-3-2 palette color
- `bmp16m`: 24-bit color
- `bmp32b`: 32-bit CMYK, outside standard BMP

## Main Behavior
- `bmp_print_page` writes a normal BMP header, then emits scan lines bottom-to-top as required by BMP.
- Scan lines are padded to 32-bit boundaries.
- `bmp_cmyk_print_page` writes four separate BMP images, one per CMYK plane, using Ghostscript render-plane support.
- Row buffers are allocated per page and freed after output.

## Dependencies
Uses `gdevprn.h`, PC color mappers from `gdevpccm.h`, and shared BMP helpers from `gdevbmp.h` / `gdevbmpc.c`.

## Notes
- Separated CMYK output is represented as multiple grayscale BMP sections in one output stream, which may not be accepted by ordinary BMP viewers as a single conventional image.
