# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdrop.c

Ghostscript default and device-independent RasterOp implementation.

Key behavior:
- Provides debug tracing for copy-rop inputs and optional bitmap dumps.
- `gx_default_strip_copy_rop` implements RasterOp for non-memory devices by reading destination pixels with `get_bits_rectangle`, running the operation in an intermediate memory device, then writing results back with `copy_color`.
- Converts source and texture colors into standard RGB/gray forms when needed.
- Special-cases conversion back into 1-bit CMYK devices.
- `mem_default_strip_copy_rop` implements RasterOp for memory devices through an 8-bit gray or 24-bit RGB intermediate memory device, expanding source/texture/destination operands as required.
- Uses stack-sized fallback buffers where possible and heap buffers for larger row blocks.
- `gx_default_copy_rop` adapts tiled texture input into strip texture input.
- `gx_copy_rop_unaligned` and `gx_strip_copy_rop_unaligned` adjust unaligned source pointers and rasters or process one scanline at a time.
- `gs_transparent_rop` computes effective ROP3 logic under source/pattern transparency rules.

Notable dependencies:
- Ghostscript ROP, memory-device, bitmap, and color APIs: `gsropt.h`, `gxdevrop.h`, `gxdevmem.h`, `gxgetbit.h`, `gdevmrop.h`.

Research notes:
- This is rendering/raster operation infrastructure, not filesystem code.
- The code carefully handles whether a ROP uses source, texture, or destination operands to avoid unnecessary reads/conversions.
- There is a likely leak/error-path issue in `gx_default_strip_copy_rop`: after copying destination data into the intermediate device, a `copy_color` failure returns immediately instead of going through the cleanup label.
- `max_rop_bitmap` intentionally limits multi-row temporary allocation, falling back to at least one row.
