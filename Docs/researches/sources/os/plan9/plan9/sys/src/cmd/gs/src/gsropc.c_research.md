# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsropc.c

## Purpose
Implements creation and partial execution of Ghostscript RasterOp compositing objects. It defines `gs_composite_rop_t` object behavior, creates a forwarding compositor device named `"RasterOp compositor"`, and routes fill/copy operations toward RasterOp-capable strip copy routines.

## Public Surface
- `gs_create_composite_rop(gs_composite_t **ppcte, const gs_composite_rop_params_t *params, gs_memory_t *mem)`: allocates a reference-counted RasterOp compositor object, assigns a new id via `gs_next_ids`, stores the logical operation and optional texture, and returns it as `gs_composite_t`.
- `c_rop_create_default_compositor(...)`: composite type hook that creates the default forwarding compositor device around a target device.

## Internal Structure
- `gs_composite_rop_type` supplies composite callbacks: create default compositor, equality, write, read, and default clist update hooks.
- `gx_device_composite_rop` extends a forwarding device with `gs_composite_rop_params_t`.
- `gs_composite_rop_device` is a device descriptor that mostly forwards device operations, while overriding close, rectangle fill, mono/color/alpha copy, and compositor creation.

## Control Flow and Behavior
- Equality compares type, `log_op`, and optional texture equality with `gx_device_color_equal`.
- Serialization callbacks `c_rop_write` and `c_rop_read` are explicitly `NYI`; callers requiring compositor serialization cannot rely on this implementation.
- `c_rop_create_default_compositor` allocates an immovable forwarding device, copies target parameters, installs the target, and stores RasterOp parameters. The code comments say memory-device specialization is intended but not implemented at compositor creation time.
- `dcr_fill_rectangle` is the main implemented imaging path. It chooses `gx_default_strip_copy_rop` by default, switches to memory RasterOp implementations for selected memory-device depths, constructs source/texture color arrays, and calls the strip-copy RasterOp procedure.
- If no texture is supplied, fill color is treated as the texture and source is implicitly absent/black. If a pure or binary-halftone texture is supplied, it is passed as the texture operand. Colored halftones and patterns are not implemented and lead to range errors or comments.
- `dcr_copy_mono`, `dcr_copy_color`, and `dcr_copy_alpha` are temporary pass-throughs to default implementations, so RasterOp composition is not fully applied for those operations here.

## Dependencies
Uses Ghostscript device, memory-device, device-color, and RasterOp internals: `gxdevice.h`, `gxdevmem.h`, `gxdcolor.h`, `gxropc.h`, and memory/type macros from the graphics library. It relies on external `mem_*_strip_copy_rop` procedures imported through `gxropc.h`/memory-device infrastructure.

## Risks and Notes
- `c_rop_write` and `c_rop_read` have no return statements in the source body shown, because they are marked `NYI`; this is a real incomplete implementation risk.
- Memory-device optimized dispatch only handles some depths; 16-bit and 32-bit paths are explicitly not implemented.
- The device under test in `dcr_fill_rectangle` is the compositor device itself, so depth/color checks rely on forwarding-device classification behavior.
- Non-pure/non-binary texture cases are incomplete, especially colored halftones and patterns.
