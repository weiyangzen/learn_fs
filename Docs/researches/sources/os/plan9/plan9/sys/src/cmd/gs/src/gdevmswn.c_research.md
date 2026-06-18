# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmswn.c

Shared Microsoft Windows 3.x display-driver support.

- `win_open` determines output size from resolution defaults, probes desktop bit depth, normalizes to 1/4/8/16/24 bpp, sets color info, and creates palettes for indexed modes.
- `win_sync_output` and `win_output_page` notify the Ghostscript DLL callback with sync/page events.
- `win_close` frees palette resources and the 8-bit mapped-color bitset.
- `win_map_rgb_color` encodes colors for 24-bit BGR, 16-bit 5:6:5, 15-bit 5:5:5, 8-bit palette mode, 4-bit PC color, or default monochrome mapping.
- 8-bit mode starts with a 64-color cube and dynamically appends up to 220 palette entries, using `mapped_color_flags` to avoid unnecessary palette scans.
- `win_map_color_rgb` decodes color indices according to the active bpp mode.
- `win_put_params` supports changing `BitsPerPixel` before open, suppresses default close/reopen during size/resolution changes, and asks the concrete implementation to reallocate its bitmap when needed.
- `win_makepalette` creates palettes for 64-, 16-, and 2-color modes.
- `win_set_bits_per_pixel` updates `color_info`, allocates or frees 8-bit mapped-color flags, installs encode/decode procs, and preserves anti-alias settings.
- Risk notes: comments admit an error-recovery path after bitmap reallocation failure is “WRONG”; code is legacy Windows API and resource-management heavy.
