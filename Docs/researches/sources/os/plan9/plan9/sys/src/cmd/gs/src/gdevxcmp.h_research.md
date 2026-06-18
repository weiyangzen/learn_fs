# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevxcmp.h

Header for the X11 color-management data embedded in `gx_device_X`.

Key contents:
- `x11_rgb_t`: reverse-map entry containing RGB values plus a defined flag.
- `x11_color_t`: dynamic color hash entry containing an `XColor` and next pointer.
- `X_color_value` aliases X color component values to `ushort`, matching Ghostscript color values.
- Optional `x11_cmap_values_t` stores precomputed standard-colormap conversion shifts and nearest-value tables.
- `x11_cman_t` groups all color state: visual RGB count, color and match masks, optional standard colormap metadata, reverse pixel-to-RGB table, dither ramp/cube pixels, and dynamic color hash table.

Notable implementation details:
- `CUBE_INDEX` indexes an RGB cube using the owning device’s `dither_colors`.
- Reverse mapping only covers pixel values up to `min(1 << depth, 256)`; larger pixels rely on colormap logic or server/query-derived structures.

Filesystem relevance:
- None.
