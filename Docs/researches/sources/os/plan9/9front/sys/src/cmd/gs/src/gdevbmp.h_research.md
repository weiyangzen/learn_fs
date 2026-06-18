# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbmp.h

## Purpose
Declares shared definitions and helper interfaces for BMP output devices.

## Contents
- Default BMP device resolution: `X_DPI 72`, `Y_DPI 72`.
- `write_bmp_header(gx_device_printer *pdev, FILE *file)`
- `write_bmp_separated_header(gx_device_printer *pdev, FILE *file)`
- 24-bit color mappers:
  - `bmp_map_16m_rgb_color`
  - `bmp_map_16m_color_rgb`

## Integration Role
Included by BMP device implementations to share header writing and 24-bit BGR color packing behavior.
