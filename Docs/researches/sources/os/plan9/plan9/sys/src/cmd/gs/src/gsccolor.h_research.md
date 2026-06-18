# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsccolor.h

Defines the client-facing Ghostscript color value structure.

Key contents:
- Includes `gsstype.h` for structure descriptor support.
- Forward-declares `gs_pattern_instance_t`.
- Defines `GS_CLIENT_COLOR_MAX_COMPONENTS` as 16.
- Defines `gs_paint_color` as an array of up to 16 float component values.
- Defines `gs_client_color` as:
  - paint values, also used for uncolored patterns
  - optional pattern instance pointer
- Declares the GC structure descriptor `st_client_color`.
- Defines `public_st_client_color()` and `st_client_color_max_ptrs`.

Important implementation notes:
- The 16-component maximum supports DeviceN-style color spaces beyond CMYK, including hexachrome and other multi-colorant devices.
- Pattern ownership is visible to Ghostscript GC through the structure descriptor.
