# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsimage.c

Implements the buffered public image enumeration layer over device image-processing callbacks.

Core model:
- `gs_image_enum` tracks memory, device, underlying image enum info, plane count, height, wanted-plane cache, retained source data, row buffers, and prepared `gx_image_plane_t` entries.
- Each plane may have a partial row buffer and/or retained source data.

Key functions:
- `gs_image_begin_typed`: obtains clip path, loads color if needed, and starts a device typed image.
- `gs_image_enum_alloc`: allocates and initializes an enumerator.
- `gs_image_init`: starts ImageType 1 images and masks, handling cachedevice and default DeviceGray cases.
- `gs_image_enum_init`: initializes from an existing lower-level image enum.
- `gs_image_planes_wanted`: reports which planes still need client data.
- `gs_image_next`: older single-plane-cycling interface.
- `gs_image_next_planes`: main multi-plane buffered data feeding routine.
- `gs_image_cleanup` and `gs_image_cleanup_and_free_enum`.

Buffering behavior:
- Partial rows are copied into stable-memory row buffers.
- Whole rows can be passed directly from caller source data.
- Retained data pointers are returned to the caller so stream-buffer clients can manage moving data.
- If wanted planes can vary, data transfer is limited to one row at a time.

Risks and quirks:
- There is an explicit note that charpath skipping is not correct for ImageType 3 InterleaveType 2.
- `gs_image_init` uses a static DeviceGray color space for parameterless images.
- Row buffers use stable memory because PostScript code may use save/restore during image data procedures.
