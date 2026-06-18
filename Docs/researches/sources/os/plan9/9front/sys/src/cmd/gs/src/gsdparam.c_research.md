# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdparam.c

This file implements default device parameter reading and writing.

Read side:
- `gs_get_device_or_hw_params` safely copies read-only prototype devices before querying.
- `gx_default_get_params` writes standard page-device parameters and Ghostscript-specific device parameters.
- `param_HWColorMap` builds a hardware color map for simple low-depth devices.
- `gx_default_get_hardware_params` returns no hardware parameters by default.

Media helpers:
- Input media: `gdev_begin_input_media`, `gdev_write_input_media`, `gdev_write_input_page_size`, `gdev_end_input_media`.
- Output media: `gdev_begin_output_media`, `gdev_write_output_media`, `gdev_end_output_media`.

Write side:
- `gs_putdeviceparams` calls the device `put_params` hook and reports whether an open device was closed.
- `gx_default_put_params` validates and applies standard parameters.

Important validation behavior:
- `HWResolution`, `HWSize`, and `MediaSize` are interdependent and applied in that order.
- `PageSize` is accepted as a backward-compatible synonym for `.MediaSize`.
- Anti-alias bits are limited to 1, 2, or 4.
- `.LockSafetyParams` cannot be unlocked once locked.
- Many nominally read-only parameters are accepted only if set to their current values.
- `param_commit` is called before mutation so unknown-parameter detection still happens even after earlier validation errors.
- Geometry/resolution/media changes close the device only if the value actually changes.
- Color caches are decached after successful parameter mutation.

This file is the default contract between page-device dictionaries and `gx_device` fields.
