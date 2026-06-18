# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmpla.h

Public interface for planar memory devices.

- Documents planar storage: bits are stored by planes, least-significant color-index plane first.
- Each plane may have a distinct supported memory-device depth, currently capped at 16 bits per plane.
- Total plane depth must fit within `gx_color_index` and within the memory device color depth.
- Planes are stored contiguously as separate device images, with one line-pointer table per plane.
- Declares `gdev_mem_set_planar(gx_device_memory *mdev, int num_planes, const gx_render_plane_t *planes)`.
- Must be called after `gs_make_mem_device` and before opening the device.
