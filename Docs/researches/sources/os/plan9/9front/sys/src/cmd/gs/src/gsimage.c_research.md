# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsimage.c

## Role

`gsimage.c` implements the buffered public image-enumerator layer above Ghostscript's lower-level typed image device interface. It accepts arbitrary chunks of image plane data, buffers partial rows, retains unused caller data by reference, and passes whole scan-line groups to image processors/devices.

This is image rendering infrastructure, not filesystem code.

## Main Interfaces

- `gs_image_begin_typed`, `gs_image_enum_alloc`, `gs_image_init`, `gs_image_enum_init`, `gs_image_bytes_per_plane_row`, `gs_image_planes_wanted`, `gs_image_next`, `gs_image_next_planes`, `gs_image_cleanup`, `gs_image_cleanup_and_free_enum`.
- Internal helpers: `image_enum_init`, `cache_planes`, `next_plane`, `begin_planes`, `gs_image_common_init`, `gs_image_row_memory`, `free_row_buffers`.

## Core Behavior

- `gs_image_begin_typed` obtains the current device and effective clip path, loads current color if needed, and calls the device typed-image begin procedure.
- `gs_image_init` handles ImageType 1 images and imagemasks, including mask color-space suppression, cachedevice restrictions, and a static DeviceGray fallback when no color space is supplied.
- Each plane tracks a stable row buffer, a partial-row position, and a retained source string.
- `gs_image_next_planes` copies partial rows into row buffers, avoids copying full rows when caller data already has enough bytes, sends complete rows through `gx_image_plane_data_rows`, updates retained data pointers and per-plane used counts, and refreshes plane-wanted state after each transfer.
- Row buffers use `gs_memory_stable` because image data procedures may perform save/restore while image processing is active.
- Passing `dev == NULL` skips drawing, used for charpath-like contexts.

## Notable Risks

- Retained source data is held by reference; clients with movable stream buffers must honor the replacement/retention contract documented in `gsimage.h`.
- A comment says the skip-data path is not correct for ImageType 3 InterleaveType 2 when mask and image heights differ.
- `gs_image_next` is a legacy cyclic single-plane API and errors if the selected plane has retained data.
- The static DeviceGray fallback is described as potentially incorrect if a non-current color space would matter, though comments say the case appears not to arise.
