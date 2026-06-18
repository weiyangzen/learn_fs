# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcmap.c

Special forwarding color-mapping device used to implement PCL5 color mapping behavior.

Key behavior:
- Defines a private prototype `gs_cmap_device` with forwarding drawing operations and custom parameter/color-mapping hooks.
- `gdev_cmap_init` initializes a `gx_device_cmap`, attaches a target device, copies target parameters, fills forwarding procs, and selects a mapping method.
- `gdev_cmap_set_method` switches among identity, monochrome, snap-to-primaries, and color-to-black-over-white modes, updating color model metadata and mapping procs.
- `cmap_get_params`/`cmap_put_params` expose `ColorMappingMethod`.
- `cmap_begin_typed_image` forwards high-level images only for identity mapping; otherwise it forces default image rendering so colors pass through the mapper.
- Gray/RGB/CMYK mapping procedures transform source color values and then delegate to the target device’s color mapping procs.

Notable dependencies:
- Ghostscript forwarding-device infrastructure, color conversion helpers, and `gdevcmap.h`.

Research notes:
- This is a device wrapper rather than a physical output device.
- CMYK mapping is explicitly noted as untested/not apparently called.
- Identity mode preserves the target color model; non-identity modes deliberately present altered color model metadata to avoid unwanted halftoning behavior.
