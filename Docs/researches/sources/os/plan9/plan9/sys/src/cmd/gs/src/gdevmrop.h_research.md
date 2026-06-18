# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmrop.h

Shared RasterOp definitions for memory-device implementations.

- Declares `gs_transparent_rop` for deriving an effective 1-bit ROP with transparency.
- Under `DEBUG`, declares `trace_copy_rop` for tracing copy/strip-copy ROP calls.
- Defines forward declarations for `gx_device_color` and `gx_device_rop_texture`.
- `gx_device_rop_texture` is a forwarding device containing a logical operation and a texture color.
- Provides the structure descriptor macro `private_st_device_rop_texture`.
- Declares allocation and initialization helpers: `gx_alloc_rop_texture_device` and `gx_make_rop_texture_device`.
- Role: supports using image data as RasterOp source while treating a specified `gx_device_color` as texture.
