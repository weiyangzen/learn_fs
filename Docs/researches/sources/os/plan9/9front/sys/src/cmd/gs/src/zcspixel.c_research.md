# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zcspixel.c

Implements DevicePixel color-space setup.

Key behavior:
- Defines `.setdevicepixelspace`.
- Accepts a two-element array, reads element 1 as an integer pixel depth, initializes a DevicePixel color space, and installs it with `gs_setcolorspace`.
- Pops the operand only after successful color-space installation.

Dependencies:
- Uses `gs_cspace_init_DevicePixel`, interpreter allocation, and graphics-state color-space APIs.

Research notes:
- This is a small adapter between PostScript color-space array syntax and the graphics-library DevicePixel color-space constructor.
