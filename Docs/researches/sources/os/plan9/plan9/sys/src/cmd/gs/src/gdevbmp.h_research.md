# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbmp.h

Shared BMP output declarations for Ghostscript BMP devices.

Key contents:
- Defines default BMP device resolution as 72 DPI in both axes.
- Declares `write_bmp_header` for standard BMP output.
- Declares `write_bmp_separated_header` for separated CMYK plane BMP output.
- Declares 24-bit color mapping procedures:
  - `bmp_map_16m_rgb_color`
  - `bmp_map_16m_color_rgb`

Notable dependencies:
- Assumes Ghostscript printer and device procedure types are already visible to the including compilation unit.

Research notes:
- This header contains only shared definitions; device descriptors live in `gdevbmp.c` and async variants in `gdevbmpa.c`.
- The 24-bit mapper explicitly supports BMP's BGR byte ordering through its implementation in `gdevbmpc.c`.
