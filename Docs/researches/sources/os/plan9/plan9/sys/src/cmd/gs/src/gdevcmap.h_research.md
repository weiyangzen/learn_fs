# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcmap.h

Public interface for the special color mapping forwarding device.

Key contents:
- Defines `gx_device_color_mapping_method_t`.
- Enumerates mapping methods: identity, snap-to-primaries, color-to-black-over-white, and monochrome.
- Defines `device_cmap_max_method`.
- Defines `gx_device_cmap` as a forwarding device plus mapping method.
- Declares GC structure support macro `public_st_device_cmap`.
- Declares `gdev_cmap_init`.

Important behavior:
- Clients may change `ColorMappingMethod` at runtime via device parameters.
- Header comments require callers to call `gs_setdevice_no_init(pgs, dev)` for every graphics state that may reference the device after changing the mapping method.

Dependencies:
- Requires Ghostscript device-forwarding types and GC macro infrastructure through includers.

Notable risks:
- The runtime-change contract is easy to miss; updating the parameter alone is not enough for existing graphics states.
- The enum order is part of the externally settable integer parameter behavior.
