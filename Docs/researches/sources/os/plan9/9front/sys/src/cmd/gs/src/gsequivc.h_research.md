# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsequivc.h

This header declares data structures and the public helper for spot-color equivalent CMYK capture.

Definitions:
- `cmyk_color` stores validity plus CMYK `frac` components.
- `equivalent_cmyk_color_params` stores global validity plus one `cmyk_color` per `GX_DEVICE_MAX_SEPARATIONS`.
- `update_spot_equivalent_cmyk_colors` updates missing equivalent CMYK colors for spot colorants when possible.

It expects `gx_device`, `gs_state`, and `gs_devn_params` types from surrounding device/color headers. The implementation is in `gsequivc.c`.
