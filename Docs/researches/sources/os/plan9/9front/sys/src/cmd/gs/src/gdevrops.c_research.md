# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevrops.c

Ghostscript forwarding helper device that supplies source/texture data for RasterOp drawing.

Key behavior:
- Defines GC enumeration and relocation for `gx_device_rop_texture`, including its embedded texture color.
- Provides `gx_alloc_rop_texture_device` and `gx_make_rop_texture_device` to allocate and initialize a RasterOp texture device over a target device.
- Copies device parameters from the target and forwards non-drawing operations to the target.
- Implements rectangle fill, monochrome copy, and color copy by wrapping incoming source data into `gx_rop_source_t`.
- Applies the stored texture and logical operation through `gx_device_color_fill_rectangle`.
- Adjusts RasterOp behavior for transparent monochrome source colors using `rop3_use_D_when_S_0` and `rop3_use_D_when_S_1`.

Notable dependencies:
- Ghostscript device/color internals: `gxdevice.h`, `gxdcolor.h`, and `gdevmrop.h`.

Research notes:
- This is a small compositing helper, not a standalone output device.
- Drawing operations are intentionally handled locally while most other operations forward.
- It is generic raster operation infrastructure, not filesystem code.
