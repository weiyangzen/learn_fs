# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwimg.h

Purpose: Declares the `IMAGE` and `IMAGE_DEVICEN` structures plus image-window APIs.

Key structures:
- `IMAGE_DEVICEN`: used/visible flags, component name, CMYK equivalent values, and menu state.
- `IMAGE`: Ghostscript handle/device, Win32 window/brush/palette state, raster format, image pointer, `BITMAPINFOHEADER`, DeviceN state, update timer state, scroll state, mutex, linked-list pointer, text-window handle, and saved window rectangle.

Public API:
- Main-thread only: `image_find`, `image_new`, `image_delete`, `image_size`.
- GUI-thread only: `image_open`, `image_close`, `image_sync`, `image_page`, `image_presize`, `image_poll`, `image_updatesize`.

Notes:
- Header declares `image_presize`, but the read implementation in `dwimg.c` does not define it.
- The shared `first_image` list is exported.

Filesystem relevance: None.
