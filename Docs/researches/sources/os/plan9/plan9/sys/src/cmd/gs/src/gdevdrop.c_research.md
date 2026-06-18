# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdrop.c

Implements default device-independent RasterOp (`copy_rop` / `strip_copy_rop`) algorithms.

For non-memory devices, `gx_default_strip_copy_rop` reads destination pixels with `get_bits_rectangle` when the RasterOp uses destination data, performs the operation on a temporary memory device, then writes results back with `copy_color`. Work is chunked by `max_rop_bitmap` to bound temporary allocation.

For memory devices, `mem_default_strip_copy_rop` converts destination/source/texture operands into standard 8-bit gray or 24-bit RGB memory-device form when needed, delegates the operation to the standard memory-device RasterOp, then packs results back into the original device format. It special-cases 1-bit CMYK packing and maps color constants through standard RGB.

The file also adapts tile-based `copy_rop` to strip texture form, handles unaligned source data by offset/raster adjustment or one-line fallback, and computes effective transparent RasterOps in `gs_transparent_rop`.

Debug builds include `trace_copy_rop` for logging operand geometry and optional bitmap dumps.

Risks: RasterOp semantics are subtle, especially transparency masking and standard/native color conversions. Temporary memory use is bounded but still allocation-dependent. Unaligned source adjustment has special cases for 24-bit data.
