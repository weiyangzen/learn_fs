# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmswn.h

Shared declarations and common structure fields for Microsoft Windows 3.x Ghostscript drivers.

- Pulls in Ghostscript core headers plus Windows compatibility headers and shell API.
- Forward-declares `gx_device_win`.
- Declares shared utility functions: `win_makepalette`, `win_nomemory`, and `win_update`.
- Declares common device procs for open, sync, output, close, RGB mapping, params, xfont, and alpha bits.
- Defines callback-style procedure typedef macros for clipboard, repaint, bitmap allocation, and bitmap freeing.
- `gx_device_win_common` adds bpp, palette state, mapped-color flags, implementation hooks, and Windows palette handles.
- Defines `gx_device_win_s` as `gx_device_common` plus Windows common fields.
- Provides initial size/resolution constants and Windows ROP constants used by rendering and xfont code.
- Defines `win_color_value` for compressing Ghostscript color values into 8-bit Windows palette components.
