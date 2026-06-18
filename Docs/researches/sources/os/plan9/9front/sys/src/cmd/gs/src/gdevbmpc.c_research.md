# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbmpc.c

## Purpose
Provides shared BMP file-format utilities and 24-bit BMP color mappers.

## Main Structures
Defines local BMP-compatible structures:
- `bmp_file_header`
- `bmp_info_header`
- `bmp_quad`

Includes endian-conversion macros so multi-byte BMP fields are written little-endian on both little- and big-endian hosts.

## Header Writing
- `write_bmp_depth_header` writes the `BM` signature, file header, info header, resolution in pixels per meter, and optional palette.
- `write_bmp_header` builds a palette for depths <= 8 by asking the device’s `map_color_rgb` proc, then delegates to `write_bmp_depth_header`.
- `write_bmp_separated_header` builds a grayscale palette for a single separated CMYK plane and writes a BMP header for that plane depth.

## Color Mapping
- `bmp_map_16m_rgb_color` packs RGB as BMP BGR byte order in a color index.
- `bmp_map_16m_color_rgb` decodes that packed value back to RGB.

## Dependencies
Uses Ghostscript printer-device APIs and declarations from `gdevbmp.h`.

## Notes
- BMP scan-line padding is handled by callers and included in header size calculations.
- The header intentionally omits the leading `BM` bytes from `bmp_file_header` to avoid compiler padding issues.
