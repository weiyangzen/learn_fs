# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdsp2.h

## Role
`gdevdsp2.h` defines the private Ghostscript device structure for the callback display device.

## Contents
- Forward-declares `gx_device_display`.
- Defines `gx_device_display_common`, adding:
  - `gx_device_memory *mdev` backing renderer.
  - `display_callback *callback`.
  - Caller handle `pHandle`.
  - Format flags `nFormat`.
  - Bitmap pointer and size.
  - `HWResolution_set`.
  - DeviceN separation parameters and equivalent CMYK color cache.
- Defines `struct gx_device_display_s` as `gx_device_common` plus the display-specific fields.
- Declares `st_device_display` GC metadata through `public_st_device_display()`.

## Dependencies and Notes
- Included by `gdevdsp.c`; depends on types from `gdevdsp.h`, memory-device code, and DeviceN/equivalent-color support.
- No behavior on its own, but it is the key shared layout between Ghostscript core device management and the display driver implementation.
