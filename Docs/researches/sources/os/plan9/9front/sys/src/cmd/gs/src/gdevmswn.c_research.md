# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmswn.c

## Role

Shared Microsoft Windows 3.x-era display driver support for Ghostscript.

## Main Functions

- `win_open` determines screen depth, sets device color info, and creates a palette if needed.
- `win_sync_output` and `win_output_page` notify `pgsdll_callback`.
- `win_close` frees palette and mapped-color tracking resources.
- `win_map_rgb_color` maps Ghostscript RGB values to Windows device pixels for 1/4/8/15/16/24 bpp.
- `win_map_color_rgb` decodes Windows device colors back to Ghostscript RGB values.
- `win_put_params` supports `BitsPerPixel` before open and limited resize/depth changes while open.
- `win_makepalette` creates standard 2/16/64-color logical palettes.
- `win_set_bits_per_pixel` sets `color_info`, palette count, mapping procs, component-index procs, and mapped-color flags.

## Data and Resource Handling

The 8-bit path starts with 64 static rrggbb colors, then dynamically appends up to 220 palette entries and tracks mapped colors in a 4096-byte bitset.

## Risks and Edge Cases

- Several comments note old behavior and one “WRONG” recovery path if bitmap reallocation fails after parameters changed.
- The code is host-platform-specific and depends on Win16/Win32 GDI types and callbacks.
- `win_close` frees resources only when `nColors > 0`; true-color modes have no palette resources.
