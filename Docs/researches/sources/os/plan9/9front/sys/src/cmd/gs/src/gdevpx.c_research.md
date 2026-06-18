# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpx.c

This file implements Ghostscript's HP PCL XL vector output devices:
- `pxlmono`: 8-bit grayscale PCL XL.
- `pxlcolor`: 24-bit RGB PCL XL.

Device state:
- `gx_device_pclxl` extends `gx_device_vector_common`.
- Tracks selected media, manual feed/media source parameters, fill/clip rules, current color space, cached palette, buffered path points, downloaded bitmap-character cache, and whether the bitmap font is selected.
- The bitmap-character cache uses a small hash table plus FIFO eviction, with limits for count, total bytes, and per-character size.

Open/page/close:
- `pclxl_open_device` opens a sequential vector output file, initializes state, writes the PCL XL/PJL file header, and initializes the character cache.
- `pclxl_beginpage` writes page header, media selection, and `BeginPage`, mapping `ManualFeed` and `%MediaSource` into PCL XL media source.
- `pclxl_output_page` emits `EndPage`, flushes, resets page state, and calls Ghostscript page completion.
- `pclxl_close_device` writes any pending `EndPage`, emits the PCL XL trailer, and closes the vector file.

Color and paint:
- `pclxl_set_color_space` and `pclxl_set_color_palette` avoid redundant color-space/palette emissions.
- `pclxl_set_color` emits gray or RGB brush/pen source, or null brush/pen.
- `pclxl_can_handle_color_space` rejects ICCBased, Separation, and Pattern spaces, and indexed spaces backed by a procedure.

Vector paths:
- Uses `gx_device_vector_procs` with custom line width, line cap/join, miter, dash, logical operation, fill/stroke color, rectangles, and path callbacks.
- Buffers line and Bezier points in `NUM_POINTS` batches.
- `pclxl_flush_points` chooses compact relative byte, signed-byte, or signed-16-bit point list encodings and emits `LinePath`, `LineRelPath`, `BezierPath`, or `BezierRelPath`.
- `pclxl_endpath` emits paint and/or clip operations with winding/even-odd handling.

Images and masks:
- `pclxl_copy_mono`, `pclxl_copy_color`, and `pclxl_fill_mask` emit direct or indexed PCL XL images.
- `pclxl_write_image_data` attempts RunLengthEncode compression for image blocks, falling back to uncompressed data if compression cannot fit the temporary buffer.
- High-level `begin_image` supports only chunky, byte-aligned, orthogonal portrait images with 1/4/8 bits per pixel; unsupported cases fall back to default Ghostscript image handling.
- `pclxl_image_plane_data` buffers rows and writes strips; `pclxl_image_end_image` flushes final rows and frees buffers.

Bitmap font optimization:
- Monochrome masks with stable `gx_bitmap_id` may be downloaded as bitmap font characters.
- `pclxl_define_bitmap_font`, `pclxl_define_bitmap_char`, and `pclxl_copy_text_char` emit font headers/chars and then draw them as text.
- This avoids repeated image emission for reused small bitmaps.

Parameters:
- `pclxl_get_params` exposes `ManualFeed`.
- `pclxl_put_params` reads `ManualFeed` and `%MediaSource`, then delegates standard vector parameters.

Notable incomplete areas:
- `pclxl_strip_copy_rop` is marked work-in-progress and returns success without emitting a general RasterOp.
- Some comments mark memory ownership or device integration as "WRONG", inherited from this Ghostscript vintage.
- High-level color handling always returns false for `pclxl_can_handle_hl_color`.
