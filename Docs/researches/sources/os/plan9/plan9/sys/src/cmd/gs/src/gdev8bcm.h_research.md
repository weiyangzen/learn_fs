# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdev8bcm.h

Header for dynamic 8-bit color-map support.

Key points:
- Documents use by MS-DOS, MS Windows, and X Windows drivers.
- Defines map size `323`, spreader `123`, no-RGB sentinel `0xffff`, and `gx_8bit_rgb_key`.
- Defines `gx_8bit_map_entry` and `gx_8bit_color_map`.
- Declares init, lookup, and add functions.
- Defines `gx_8bit_map_is_full`.

Dependencies and interactions:
- Requires `gxdevice.h` for `gx_color_value`.
- Paired with `gdev8bcm.c`.

OS/filesystem relevance:
- None; display color-cache data structures only.
