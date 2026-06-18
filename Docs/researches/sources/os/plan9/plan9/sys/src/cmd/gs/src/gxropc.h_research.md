# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxropc.h

`gxropc.h` defines internal RasterOp compositing objects. It includes `gsropc.h` for RasterOp parameters and `gxcomp.h` for composite common fields.

`gs_composite_rop_t` embeds `gs_composite_common` and stores `gs_composite_rop_params_t params`. `private_st_composite_rop()` supplies GC metadata, especially for `params.texture`.

The only declared procedure is `gx_init_composite_rop`, which initializes a stack- or heap-allocated RasterOp compositing object from parameter data. The comment explains why this initializer is exposed: clients can allocate `gs_composite_rop_t` on the stack to avoid memory-manager overhead.

Implementation is in `gsropc.c`. This header is small but important for compositing paths that need RasterOp state without dynamic allocation.
