# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevps.c

## Purpose
Implements Ghostscript’s `pswrite` and `epswrite` PostScript-writing vector devices. It converts Ghostscript graphics operations into compact PostScript/EPS output, including document/page structure, paths, colors, masks, bitmaps, high-level images, image caching, and DSC-safe binary data emission.

## Main Structures And Devices
- `gx_device_pswrite`: extends `gx_device_psdf_common` with PostScript writer parameters, page state, an image binary writer, fixed-size image cache, deferred page-fill tracking, and compact path state.
- `gs_pswrite_device`: normal PostScript writer device.
- `gs_epswrite_device`: EPS writer with `ProduceEPS` enabled.
- `psw_path_state_t`: tracks compact path/polygon output and operand-stack limits.
- `psw_image_params_t`: stores cached bitmap id, bit width, and height.

## Key Behavior
- Defines PostScript ProcSet fragments for compact color, path, rectangle, clipping, image, ASCII85/hex, and CCITT Fax operators.
- Emits file/page headers and trailers through `psw_begin_file`, `psw_write_page_header`, `psw_write_page_trailer`, and `psw_end_file`.
- Supports separate-page output filenames by closing and reopening the vector output stream per page.
- Defers initial erasepage-like rectangle fills until page content begins, preserving transfer-function behavior.
- Emits compact path syntax by rounding coordinates to two decimals, batching line deltas, using shortcuts for repeated/reversed deltas, and flushing before operand-stack assumptions are exceeded.
- Implements `fill_rectangle`, `copy_mono`, `copy_color`, `fill_path`, `stroke_path`, `fill_mask`, and high-level image enumeration.
- Writes image data through psdf binary writer filters, choosing ASCIIHex/ASCII85/binary and bracketing binary data with DSC `%%BeginData` / `%%EndData`.
- Maintains a small open-addressed image cache for reusable small bitmap/image data.
- Falls back to default Ghostscript image handling for unsupported image formats, color spaces, decode arrays, indexed-color cases, and high-level color cases.

## Dependencies
Uses vector-device infrastructure, bbox devices, Ghostscript stream filters, ASCII85/hex encoders, CCITT Fax encoding, `gdevpsdf.h` / `gdevpsdu.c` common psdf utilities, and PostScript header helpers from `gdevpsu.h`.

## Research Notes
This is the concrete PostScript vector writer front end. The risk surface is mostly stream-state correctness and fallback behavior: unsupported high-level color is rejected, some image support is intentionally narrow, and binary images are buffered to compute DSC byte counts before output.
