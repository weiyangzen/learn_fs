# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpx.c

This file implements Ghostscript's HP PCL XL vector output devices:
- `pxlmono`: 8-bit grayscale PCL XL.
- `pxlcolor`: 24-bit RGB PCL XL.

`gx_device_pclxl` extends `gx_device_vector_common` with selected media state, `ManualFeed` and `%MediaSource` handling, current fill/clip rules, cached PCL XL color space/palette state, buffered path points, a downloaded bitmap-character cache, and a flag recording whether the bitmap font is selected.

Open/page/close flow:
- `pclxl_open_device` opens a sequential vector output file, initializes vector procedures and page state, writes the PCL XL/PJL file header, and initializes the bitmap-character cache.
- `pclxl_beginpage` writes page orientation, media size/source selection, and `BeginPage`, mapping `ManualFeed` and `%MediaSource` into PCL XL media source values.
- `pclxl_output_page` emits `EndPage`, flushes, resets page state, and completes Ghostscript page output.
- `pclxl_close_device` writes a pending `EndPage` if needed, emits the PCL XL trailer, and closes the vector file.

Color and paint handling:
- `pclxl_set_color_space` and `pclxl_set_color_palette` suppress redundant color-space/palette emissions.
- `pclxl_set_color` emits gray, RGB, null brush, or null pen source commands.
- `pclxl_can_handle_color_space` rejects ICCBased, Separation, Pattern, and procedure-backed Indexed spaces.
- `pclxl_set_paints` synchronizes brush/pen nulling and fill-rule state before painting paths.

Vector path handling:
- `pclxl_vector_procs` supplies callbacks for line width, caps, joins, miter limit, dash, logical operation, fill/stroke colors, rectangles, and path construction.
- `pclxl_flush_points` batches line and Bezier points in `NUM_POINTS` buffers, choosing compact relative byte, signed-byte, or signed-16-bit point-list encodings before emitting `LinePath`, `LineRelPath`, `BezierPath`, or `BezierRelPath`.
- `pclxl_endpath` emits paint and/or clip operations, including even-odd vs nonzero winding updates.

Images and masks:
- `pclxl_copy_mono`, `pclxl_copy_color`, and `pclxl_fill_mask` emit PCL XL images for direct or indexed raster data.
- `pclxl_write_image_data` tries RunLengthEncode compression for image blocks, falling back to uncompressed data if allocation fails or compression does not fit the temporary buffer.
- High-level `pclxl_begin_image` accepts only chunky, byte-aligned, orthogonal portrait images with 1, 4, or 8 bits per pixel; unsupported cases fall back to Ghostscript default image handling.
- `pclxl_image_plane_data` buffers rows into strips, and `pclxl_image_end_image` flushes final rows and frees buffers.

Bitmap font optimization:
- Monochrome masks with stable `gx_bitmap_id` can be downloaded as bitmap font characters.
- `pclxl_define_bitmap_font`, `pclxl_define_bitmap_char`, and `pclxl_copy_text_char` define and reuse cached glyph bitmaps as PCL XL text, avoiding repeated image emission for small reused masks.
- The cache uses open addressing plus FIFO eviction with caps for character count, total bytes, and per-character byte size.

Parameters:
- `pclxl_get_params` exposes `ManualFeed`.
- `pclxl_put_params` reads `ManualFeed` and `%MediaSource`, delegates standard vector parameters, and records which page/media inputs were explicitly set.

Notable incomplete areas:
- `pclxl_strip_copy_rop` is marked work-in-progress and returns success without emitting general RasterOp output.
- Some comments mark vector-device memory integration as "WRONG", reflecting this Ghostscript vintage.
- High-level color handling through `pclxl_can_handle_hl_color` always returns false.
