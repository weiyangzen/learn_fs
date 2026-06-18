# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsimage.h

Public generic image rendering interface.

Documents the buffering contract between clients and the underlying device image processor:
- Client data may be incomplete, unaligned, multi-plane, or selectively supplied.
- `gs_image_next_planes` consumes bytes and may retain source data by reference.
- `gs_image_planes_wanted` reports only planes that the lower layer wants and that lack a full buffered row.

Exports:
- `gs_image_begin_typed`
- `gs_image_enum_alloc`
- `gs_image_init`
- `gs_image_enum_init`
- `gs_image_bytes_per_plane_row`
- `gs_image_planes_wanted`
- `gs_image_next_planes`
- `gs_image_next`
- cleanup routines

The header also warns that `gs_image_next` is only suitable for simpler cases where all planes are always wanted and have compatible dimensions/depths.
