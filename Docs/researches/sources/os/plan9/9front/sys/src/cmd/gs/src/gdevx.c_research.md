# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevx.c

Main Ghostscript X11 display renderer. It defines public X devices `x11` and `x11alpha` and implements the drawing/update operations; initialization and color management are split into companion files.

Key responsibilities:
- Device descriptors wire Ghostscript device procedures to X11 operations.
- `x_open` / `x_close` delegate lifecycle to `gdev_x_open` / `gdev_x_close`.
- `x_sync`, `x_output_page`, and `gdev_x_send_event` flush display output and coordinate with Ghostview client messages.
- `x_fill_rectangle`, `x_copy_mono`, `x_copy_color`, and `x_copy_image` render fills and image transfers into the destination window/pixmap.
- `x_strip_tile_rectangle` maps Ghostscript halftone tiles into X pixmaps and uses tiled fills when possible.
- `x_begin_typed_image` optimizes ImageType 2 `PixelCopy` with X `CopyArea` when source/destination devices and transforms match.
- `x_get_bits_rectangle` reads pixels back with `XGetImage`, normalizing supported 16/24-bit server layouts.
- Update machinery (`update_init`, `x_update_add`, `update_do_flush`) coalesces writes and copies from backing pixmap or memory buffer to the visible window.
- BBox callback procs integrate buffered rendering with Ghostscript’s bounding-box device.
- `alt_put_image` emulates a subset of `XPutImage` with rectangles for broken X servers.

Notable implementation details:
- Transparent mono writes have optimized boolean-function cases (`GXand`/`GXor`) and a hard path using a 1-bit clip pixmap.
- The renderer tracks `colors_or`/`colors_and` to optimize monochrome writes over known-color regions.
- Backing pixmap and memory-buffer modes affect when writes hit the visible window.
- Text buffering is flushed before graphics operations that would invalidate GC assumptions.

Filesystem relevance:
- None beyond being part of the Ghostscript source tree.
