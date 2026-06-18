# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcmap.h

Public interface for the special color mapping forwarding device.

Key contents:
- `gx_device_color_mapping_method_t` enum:
  - `device_cmap_identity`
  - `device_cmap_snap_to_primaries`
  - `device_cmap_color_to_black_over_white`
  - `device_cmap_monochrome`
- `gx_device_cmap` struct extending `gx_device_forward_common` with a `mapping_method`.
- GC structure declaration macro `public_st_device_cmap`.
- Prototype for `gdev_cmap_init`.

Research notes:
- Comments state that clients may change `ColorMappingMethod` at runtime but must then call `gs_setdevice_no_init` for graphics states referencing the device.
