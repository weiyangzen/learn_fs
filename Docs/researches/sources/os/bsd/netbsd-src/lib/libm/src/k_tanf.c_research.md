# File Research: sources/os/bsd/netbsd-src/lib/libm/src/k_tanf.c

This file implements the float tangent kernel `__kernel_tanf(float x, float y, int iy)`.

It mirrors the double tangent kernel with float constants: tiny input handling, transformation near `pi/4`, odd polynomial approximation, and either tangent or compensated reciprocal output depending on `iy`.

Dependencies include float word macros, local `pio4`/`pio4lo`, and tangent coefficient tables.
