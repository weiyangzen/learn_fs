# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcdevn.h

Internal DeviceN color-space support header. It defines `gs_device_n_map`, a reference-counted one-entry cache for DeviceN tint conversion. The structure stores a tint-transform callback, callback data, a validity flag, the last input tint array, and cached concrete component values sized by `GX_DEVICE_COLOR_MAX_COMPONENTS`.

The header exports the GC descriptor macro `private_st_device_n_map`, allocation API `alloc_device_n_map`, and `using_alt_color_space`, which tells callers whether rendering is using the alternate color space. It depends on `gsrefct.h` for `rc_header` and `gxcindex.h` for the maximum device component count. This is a narrow shared interface used by DeviceN color implementation code rather than a standalone algorithm.
