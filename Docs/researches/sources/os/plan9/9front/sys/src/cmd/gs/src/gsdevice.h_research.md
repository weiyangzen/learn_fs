# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdevice.h

This header declares the public device and page-control API.

It forward-declares `gx_device`, `gx_device_memory`, `gs_matrix`, `gs_param_list`, `gs_imager_state`, and `gs_state`, then exposes functions for:
- Opening, closing, copying, and querying devices.
- Creating memory/image devices.
- Getting initial matrices and device names.
- Reading and writing device/hardware parameters.
- Updating device parameters with imager or graphics state side effects.
- Flushing/copying/outputting pages.
- Selecting null/current devices.
- Setting devices with or without erase/init behavior.

Notable API distinctions:
- `gs_copydevice2` can preserve open state if `keep_open` is true, but comments warn this is risky.
- `gs_setdevice_no_erase` returns `1` when `erasepage` is required.
- `gs_setdevice_no_init` changes device without reinitializing CTM/clipping state.
- `gs_imager_putdeviceparams` updates color mapping after parameter changes.

Potential maintenance note: the `gs_initialize_imagedevice` macro appears to pass `color_size`, while its macro parameter is named `colors_size`.
