# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcspixel.c

Implements DevicePixel color space setup.

`.setdevicepixelspace` expects a two-element array, reads element 1 as an integer depth, initializes a DevicePixel color space through `gs_cspace_init_DevicePixel()`, and installs it with `gs_setcolorspace()`.

This is a small adapter from PostScript array operands to the graphics library DevicePixel color-space constructor. On success it pops the operand array; otherwise it propagates the graphics-library error.

Registered in `zcspixel_op_defs`.
