# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsimage.h

## Role

`gsimage.h` declares Ghostscript's generic buffered image rendering interface.

This is image API infrastructure, not filesystem code.

## Main Declarations

- Opaque `gx_image_enum_common_t` and `gs_image_enum`.
- `gs_image_begin_typed`, `gs_image_enum_alloc`, `gs_image_init`, `gs_image_enum_init`, `gs_image_bytes_per_plane_row`, `gs_image_planes_wanted`, `gs_image_next_planes`, `gs_image_next`, `gs_image_cleanup`, `gs_image_cleanup_and_free_enum`.

## Important Contract

The header carefully defines how `gs_image_next_planes` differs from the low-level `plane_data` procedure: data can be unaligned, incomplete, supplied per selected planes, and retained by reference. If data is retained, later data for that plane replaces rather than appends to retained data unless the client passes no replacement.

## Notable Risks

The older `gs_image_next` API is only safe for image types where all planes are always wanted, share width/depth, and receive equal data per cycle; this is documented but not fully checked.
