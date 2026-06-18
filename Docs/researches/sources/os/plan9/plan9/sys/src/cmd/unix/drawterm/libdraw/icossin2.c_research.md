# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/icossin2.c

Computes scaled sine/cosine for a vector `(x, y)` using tangent lookup tables and interpolation.

Key data/function:
- `sinus[]` and `cosinus[]`: values for `sin(atan(t))` and `cos(atan(t))`, scaled to `1024`.
- `icossin2`: handles axis-aligned vectors, sign correction, slope selection, table lookup, and linear interpolation.

Used by wide line rendering to compute perpendicular offsets and arrowhead geometry.
