# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmr2n.c

RasterOp adapter for 2- and 4-bit gray memory devices.

- Main entry point is `mem_gray_strip_copy_rop`.
- Attempts to fake 2-/4-bit gray ROPs by expanding pixel coordinates into equivalent 1-bit spans and reusing `mem_mono_strip_copy_rop`.
- Falls back to `mem_default_strip_copy_rop` for color devices, transparency, unsupported source palettes, or incompatible texture colors.
- Adjusts source colors, texture geometry, phase, width, and device width by `log2_depth`.
- Fabricates a tiny texture for constant non-black/non-white texture colors.
- Temporarily replaces `fill_rectangle`, `copy_mono`, and `strip_tile_rectangle` with stub routines that force fallback if mono ROP special cases are used.
- Restores device procedures and width after the mono call.
- Risk notes: temporary mutation of `dev->width` and procedure slots is fragile; the stub routines intentionally return errors to trigger the slow general path.
