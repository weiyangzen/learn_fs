# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsropc.h

## Purpose
Declares the RasterOp compositing interface used by Ghostscript clients that want to create a logical-operation compositor with an optional texture operand.

## Public Surface
- `gs_composite_rop_params_t`: packs `gs_logical_operation_t log_op` and `const gx_device_color *texture`.
- `gs_create_composite_rop(...)`: factory for `gs_composite_t` RasterOp compositor objects.

## Semantics
- If `texture == 0`, input data are used as the texture and source is implicitly black/zero.
- If `texture != 0`, the texture pointer supplies the texture operand and input data are the source.
- The caller promises the pointed-to texture will not change while used by the compositor.

## Dependencies
Includes `gscompt.h` for generic compositors and `gsropt.h` for logical operation/RasterOp definitions. It forward-declares `gx_device_color` when needed.

## Risks and Notes
- The texture pointer is borrowed and immutable by contract, not owned or copied by the interface. Lifetime violations would affect rendering correctness and equality checks.
