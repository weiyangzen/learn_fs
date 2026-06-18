# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdevice.h

## Role

`gsdevice.h` is the public API for Ghostscript device and page control.

## Exposed Interfaces

Device-only operations include opening, closing, copying, querying known devices, copying scanlines, reading/writing parameters, getting device name, and initial matrix retrieval.

Image-device creation is exposed through:

- `gs_makeimagedevice`
- `gs_makewordimagedevice`
- `gs_initialize_wordimagedevice`

Graphics-state operations include page flush/copy/output, null device selection, setting devices with or without erase/init behavior, retrieving current device, and updating current-device parameters.

## Types

Forward-declares `gx_device`, `gx_device_memory`, `gs_matrix`, `gs_param_list`, `gs_imager_state`, and `gs_state`.

## Compatibility

Provides macros for `gs_getdeviceparams`, `gs_gethardwareparams`, and backward-compatible `gs_get_device_or_hardware_params`.

## Risks

One macro appears inconsistent: `gs_initialize_imagedevice` passes `color_size`, while the macro parameter is `colors_size`. If used as written, that macro depends on an external `color_size` symbol or fails to compile. Most call sites likely use `gs_initialize_wordimagedevice` directly.
