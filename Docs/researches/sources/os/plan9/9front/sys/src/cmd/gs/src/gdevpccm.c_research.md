# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpccm.c

## Purpose

`gdevpccm.c` provides shared PC-style color mapping helpers used by Ghostscript PCX, 2-up PCX, and EGA/VGA-related devices.

## Functions

`pc_4bit_map_rgb_color` maps RGB values to an EGA/VGA 4-bit color index where bits represent intensity, red, green, and blue. The implementation effectively uses eight RGB colors and turns on the intensity bit for all non-black colors. `pc_4bit_map_color_rgb` reverses the mapping to full-intensity component values based on the RGB bits.

`pc_8bit_map_rgb_color` maps RGB to a 6x6x6 fixed palette index, yielding 216 colors. `pc_8bit_map_color_rgb` reverses that index using a six-step ramp and maps indexes outside 0..215 to black.

`pc_write_palette` writes `max_index` palette entries to a `FILE *` by calling the device's `map_color_rgb` proc and downshifting each component to 8 bits.

## Dependencies

The file includes Ghostscript core/device headers and its own interface `gdevpccm.h`. It is consumed by `gdevpcx.c`, `gdevp2up.c`, and PC framebuffer code.

## Filesystem Relevance

Only palette bytes are written to a caller-supplied `FILE *`; there is no filesystem logic.

## Risks and Notes

The 8-bit palette deliberately uses only 216 of 256 entries so halftoning sees symmetric component counts. Out-of-range palette reads decode to black, which is safe for malformed indexes but may hide upstream errors.
