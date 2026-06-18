# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcdevn.h

Internal DeviceN color-space support header.

Key behavior:
- Defines `gs_device_n_map`, a reference-counted one-entry cache for DeviceN tint transforms.
- Stores the tint transform callback, callback data, cache-valid flag, last tint component values, and concrete device component fractions.
- Provides the private GC descriptor macro for relocating `tint_transform_data`.
- Declares allocation/initialization through `alloc_device_n_map`.
- Declares `using_alt_color_space`, which reports whether the current graphics state is using the alternate color space.

Dependencies:
- Includes Ghostscript reference-count support and `gxcindex.h` for `GX_DEVICE_COLOR_MAX_COMPONENTS`.
- Depends on `GS_CLIENT_COLOR_MAX_COMPONENTS`, `gs_imager_state`, `gs_state`, and Ghostscript client-name/memory types from surrounding headers.

Research notes:
- The cache is explicitly a single-entry optimization, not a general tint-transform memo table.
- This header only defines the internal data contract; implementation lives in DeviceN color-space code outside this group.
