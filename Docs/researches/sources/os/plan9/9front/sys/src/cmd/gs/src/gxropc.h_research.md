# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxropc.h

Internal RasterOp compositing object declaration.

Key contents:
- Includes public RasterOp compositing parameters from `gsropc.h` and base compositor declarations from `gxcomp.h`.
- Defines `gs_composite_rop_t` as `gs_composite_common` plus `gs_composite_rop_params_t`.
- Declares the GC descriptor macro for `params.texture`.
- Declares `gx_init_composite_rop`, allowing callers to initialize stack-allocated RasterOp compositors.

Notable dependencies:
- `gsropc.h` for RasterOp parameters.
- `gxcomp.h` for compositor common fields.

Research notes:
- The comments explicitly justify exposing initialization so clients can avoid memory-manager overhead by stack-allocating compositor objects.
