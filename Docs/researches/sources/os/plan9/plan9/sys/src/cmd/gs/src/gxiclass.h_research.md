# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxiclass.h

Purpose: defines the abstract image rendering class callback interface.

Key declarations:
- Forward declares `gx_image_enum` and `gx_device`.
- Defines `irender_proc_t`: renders expanded complete source rows for an image enumerator.
- Defines `gx_image_class_t`: selects a renderer for an image class and may update the enumerator.

Contract details:
- Render procedures receive a buffer, data x offset, sample count width, height, and target device.
- `w` is sample count, not pixel count or byte count.
- `h == 0` signals end-of-input flushing.
- Render procedures return a negative error code or the number of rows processed.

Research notes:
- This header underpins files such as `gxifast.c`, `gxicolor.c`, and `gxi12bit.c`, whose strategy functions compete in priority order.
