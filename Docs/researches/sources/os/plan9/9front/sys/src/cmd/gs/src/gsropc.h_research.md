# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsropc.h

Declares the public RasterOp-compositing interface.

Key definitions:
- `gs_composite_rop_params_t` holds a packed logical operation and optional `gx_device_color` texture.
- The comments define two operating modes: no texture means input data are treated as texture with implicit black source; non-null texture means input data are source and the caller promises the texture is stable.
- `gs_create_composite_rop` constructs a compositor object from those parameters.

Dependencies:
- Includes `gscompt.h` for compositor types and `gsropt.h` for logical RasterOp definitions.
- Forward-declares `gx_device_color` when needed.
