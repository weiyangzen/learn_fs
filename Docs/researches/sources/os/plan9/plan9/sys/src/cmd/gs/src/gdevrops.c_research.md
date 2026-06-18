# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevrops.c

Purpose: Implements a small forwarding “RasterOp source” device used to combine a target device, texture device color, source pixels, and a logical operation.

Key behavior:
- Defines GC enum/relocation support for `gx_device_rop_texture`.
- Provides `gx_alloc_rop_texture_device` and `gx_make_rop_texture_device` to allocate and initialize the wrapper around a target device.
- The device forwards non-drawing operations to the target and intercepts rectangle fill, mono copy, and color copy.
- `rop_texture_fill_rectangle` builds a constant-color source and calls `gx_device_color_fill_rectangle`.
- `rop_texture_copy_mono` builds a bitmap source and adjusts the logical operation when either mono color is transparent.
- `rop_texture_copy_color` builds a color bitmap source with `use_scolors = false`.

Important dependencies:
- Ghostscript device/color internals: `gxdcolor.h`, `gxdevice.h`, `gdevmrop.h`.

Notable risks / findings:
- This file is infrastructure-only and has no filesystem relevance beyond being part of the Plan 9 Ghostscript source tree.
- Correctness depends on the target device and `gx_device_color_fill_rectangle` honoring the composed RasterOp semantics.
