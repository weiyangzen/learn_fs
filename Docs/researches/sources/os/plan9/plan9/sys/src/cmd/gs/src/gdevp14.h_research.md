# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevp14.h

This header defines the public/internal structures and entry points for the PDF 1.4 transparency rendering device implemented in `gdevp14.c`.

It declares `pdf14_default_colorspace_t` with `DeviceGray`, `DeviceRGB`, and `DeviceCMYK`, matching the default blending-space choices used by the compositor. The central structure is `pdf14_buf`, a saved-buffer stack node containing group flags (`isolated`, `knockout`), compositing state (`alpha`, `shape`, `blend_mode`), flags for extra planes, rectangle bounds, row/plane strides, total channel/plane counts, image data, optional mask transfer function, and a touched bounding box. Pixel data is explicitly documented as planar: pixel values, alpha, optional shape, optional `alpha_g`.

`pdf14_ctx` owns the current buffer stack, an optional pending mask buffer, allocator, device rectangle, additive/subtractive polarity, and channel count. `pdf14_device` extends `gx_device_forward_common`, adds the active transparency context, current opacity/shape/alpha/blend mode, saved color-mapping callback, and saved clist color info.

The exported functions are `gs_pdf14_device_push`, which installs a PDF 1.4 compositor device over a target device, and `send_pdf14trans`, which creates and sends a PDF 1.4 transparency compositor operation to a device.
