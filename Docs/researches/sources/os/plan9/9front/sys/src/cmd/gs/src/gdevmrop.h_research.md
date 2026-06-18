# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmrop.h

## Role

Shared definitions for memory-device RasterOp implementations and RasterOp texture forwarding devices.

## Main APIs

- `gs_transparent_rop(gs_logical_operation_t lop)` computes effective RasterOp with transparency.
- Debug-only `trace_copy_rop` traces copy/strip RasterOp calls.
- Defines `gx_device_rop_texture`, a forwarding device carrying a logical operation and `gx_device_color` texture.
- Declares GC structure helper macro `private_st_device_rop_texture`.
- Declares:
  - `gx_alloc_rop_texture_device`
  - `gx_make_rop_texture_device`

## Design Notes

The `gx_device_rop_texture` device supports PostScript behavior where colors act as RasterOp texture, and image data may need to act as the source for `CombineWithColor`.

## Research Notes

Header-only support shared by RasterOp C files and `gdevrops.c`.
