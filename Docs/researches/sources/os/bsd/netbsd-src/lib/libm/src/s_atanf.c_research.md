# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_atanf.c

This file implements public float `atanf(float x)`.

It is the float counterpart of `s_atan.c`: reduce to one of several intervals, evaluate the odd polynomial split into even and odd powers, add interval constants, restore sign, return `+/-pi/2` for very large finite inputs, and propagate NaN.

It weak-aliases `atanf` to `_atanf`. Dependencies include `fabsf`, float word extraction, and local float coefficient tables.
