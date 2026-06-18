# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevplnx.h

This header declares the plane extraction device implemented in `gdevplnx.c`. It describes the purpose and constraints of `gx_device_plane_extract`: to appear like a normal color-capable target while rendering only one selected color plane into another device.

The main structure embeds `gx_device_forward_common`, then stores a `gx_device *plane_dev`, a `gx_render_plane_t plane`, computed open-time fields `plane_white`, `plane_mask`, and `plane_dev_is_memory`, plus the dynamic `any_marks` optimization flag. The comments explain that the original use case is band-list rendering for plane-oriented color printers, where each plane is rasterized separately and operations writing only white can often be skipped before any non-white mark appears.

The header also declares `public_st_device_plane_extract()` for Ghostscript structure/GC metadata and exposes:

- `plane_device_init(gx_device_plane_extract *edev, gx_device *target, gx_device *plane_dev, const gx_render_plane_t *render_plane, bool clear)`

The documented depth constraints are important for callers: target and plane-extract depths are limited to 32 bits, while each extracted plane is limited to 8 bits.

Filesystem relevance: none directly. It is printer/raster device infrastructure, especially for banded and planar rendering.
