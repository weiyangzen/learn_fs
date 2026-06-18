# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdevrop.h

Small RasterOp extension header.

- Declares unaligned implementations:
  - `gx_copy_rop_unaligned`
  - `gx_strip_copy_rop_unaligned`
- Uses `dev_proc_copy_rop` and `dev_proc_strip_copy_rop` macros from the device interface.

Role: exposes slower but more flexible RasterOp copy paths for data that does not meet the normal alignment requirements.
