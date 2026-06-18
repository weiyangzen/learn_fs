# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbj10.c

## Purpose
Implements Canon Bubble Jet BJ-10e/BJ-200/BJ-300-style monochrome printer drivers.

## Devices
- `gs_bj200_device`: 360 dpi `bj200`
- `gs_bj10e_device`: 360 dpi `bj10e`

## Main Behavior
- `bj200_open` and `bj10e_open` choose margins based on paper width, distinguishing A4-like and letter-like pages.
- `bj10e_print_page` initializes the printer, disables automatic carriage return, sets vertical spacing and printable page length, then sends raster data in print-head-height strips.
- Output is transposed from scan-line order into column/jet order using `gdev_prn_transpose_8x8`.
- Blank scan lines are skipped with vertical tab commands.
- Blank horizontal column groups are skipped with printer horizontal skip commands.
- The final print pass is aligned so the bottom of the print head reaches the desired bottom margin.

## Printer Protocol
- Uses ESC/P-style BJ commands:
  - reset/set initial conditions
  - disable automatic CR
  - vertical spacing
  - page length
  - vertical/horizontal skips
  - raster graphics transfer
  - form feed

## Notes
- The large comments document BJ200 factory defaults, DIP switch implications, BJ300 compatibility, and margin behavior.
- `USE_FACTORY_DEFAULTS` can change reset behavior for letter/A4 handling.
- Memory use is limited to one input line buffer and one transposed output strip buffer.

## Dependencies
Uses Ghostscript printer device helpers from `gdevprn.h`.
