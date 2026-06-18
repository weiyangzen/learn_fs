# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbmpc.c

Shared BMP file-format utility implementation for Ghostscript BMP devices.

Key behavior:
- Defines local BMP file header, info header, and RGB quad structures, with explicit little-endian assignment macros for big-endian hosts.
- `write_bmp_depth_header` writes the `BM` signature, file header, info header, optional palette, image dimensions, row stride, pixel depth, and resolution in pixels per meter.
- `write_bmp_header` builds a palette for depths up to 8 bits by calling the device's color decode routine, then delegates to `write_bmp_depth_header`.
- `write_bmp_separated_header` builds a grayscale inverted palette for a single CMYK separation plane.
- `bmp_map_16m_rgb_color` and `bmp_map_16m_color_rgb` encode/decode 24-bit BMP color indexes in Windows BGR byte order.

Notable dependencies:
- Ghostscript printer/device APIs through `gdevprn.h`.
- Declarations from `gdevbmp.h`.

Research notes:
- The file explicitly avoids including the `BM` bytes inside `bmp_file_header` because compiler padding could shift the following 32-bit field.
- Palette writing uses `fwrite` but does not check its return value, unlike the fixed headers.
- 32-bit CMYK-like output is supported by callers but is outside standard BMP semantics; this utility only writes an uncompressed BMP-style header for the given depth.
