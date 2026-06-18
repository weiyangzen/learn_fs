# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdevrop.h

This tiny header extends the device interface for RasterOp support by declaring unaligned implementations of `copy_rop` and `strip_copy_rop`.

It relies on the `dev_proc_copy_rop` and `dev_proc_strip_copy_rop` macros from the device headers. The two declarations are `gx_copy_rop_unaligned` and `gx_strip_copy_rop_unaligned`.

Filesystem relevance: none. This is raster-compositing support.
