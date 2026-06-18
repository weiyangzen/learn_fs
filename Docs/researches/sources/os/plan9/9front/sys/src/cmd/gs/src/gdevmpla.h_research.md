# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmpla.h

## Role

Public interface and representation notes for planar memory devices.

## Key API

- Declares `gdev_mem_set_planar(gx_device_memory *mdev, int num_planes, const gx_render_plane_t *planes)`.

## Design Contract

- Planes store bits separately rather than chunky pixels.
- Least-significant color-index plane is stored first.
- Each plane has a supported memory-device depth, currently documented as 1, 2, 4, 8, or 16.
- Data for each plane is contiguous as if each plane were an independent memory device.
- There is one line-pointer array per plane.

## Research Notes

Header-only contract; implementation is in `gdevmpla.c`.
