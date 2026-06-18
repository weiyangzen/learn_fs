# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsropc.c

Implements the Ghostscript RasterOp compositor object and a forwarding compositor device used to apply logical RasterOp operations during rendering.

Key behavior:
- Defines the `gs_composite_rop_type` compositor vtable and allocates `gs_composite_rop_t` objects in `gs_create_composite_rop`.
- Compares RasterOp compositors by operation code and optional texture device color.
- Creates a `gx_device_composite_rop` wrapper device around a target device in `c_rop_create_default_compositor`.
- Overrides fill/copy procs for the wrapper; most image/copy paths temporarily fall back to default implementations.
- `dcr_fill_rectangle` maps flat fills to `strip_copy_rop`, selecting memory-device helpers for selected depths and handling pure or binary-halftone textures.

Dependencies:
- Uses compositor, device, device-color, memory-device, and RasterOp support from `gxcomp`, `gxdevice`, `gxdcolor`, `gxdevmem`, and `gxropc`.
- Uses `gs_next_ids` for compositor identity.

Research notes:
- Serialization hooks `c_rop_write` and `c_rop_read` are explicitly `NYI` and contain no return path in this source.
- Several rendering paths are also marked incomplete: memory device selection, 16/32-bit implementations, colored halftones, patterns, and identity-operation bypass.
