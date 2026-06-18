# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmswn.h

## Role

Shared definitions for Microsoft Windows Ghostscript display drivers.

## Main Contents

- Includes Ghostscript core headers plus Windows headers and `gp_mswin.h`.
- Declares `gx_device_win`.
- Declares utility functions: `win_makepalette`, `win_nomemory`, `win_update`.
- Declares shared device procedures for open, sync, output, close, color mapping, params, xfont, and alpha bits.
- Defines callback-like implementation hooks for bitmap allocation/free and repaint/copy.
- Defines `gx_device_win_common`, embedded in `gx_device_win_s`.
- Defines initial resolution and page dimensions.
- Defines Windows RasterOp constants and `win_color_value` compression macro.

## Research Notes

Platform header only. It bridges Ghostscript device abstractions to Windows GDI resource types.
