# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/rgbycc.c

Table generator for YCbCr/RGBV conversion support. It computes Plan 9 colormap entries nearest to YCbCr-derived RGB colors and prints generated C tables.

The output includes `ycbcrmap[256]`, converting palette entries to YCbCr-like packed values, and `closestycbcr[16*16*16]`, a coarse nearest-palette lookup table. The code uses floating-point YCbCr formulas and edge guards for high-end Y/Cb/Cr values.

This file feeds generated lookup headers used by runtime remapping code such as `torgbv.c`.
