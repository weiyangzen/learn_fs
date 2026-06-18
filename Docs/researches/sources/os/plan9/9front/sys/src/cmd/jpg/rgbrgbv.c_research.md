# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/rgbrgbv.c

Table generator for RGB to Plan 9 RGBV palette mapping. It computes nearest Plan 9 colormap entries using squared RGB distance against `cmap2rgb`.

`main` prints two C initializers: `rgbmap[256]`, mapping palette indices to RGB triples, and `closestrgb[16*16*16]`, mapping 4-bit-per-channel RGB cubes to nearest palette indices.

This is a build/helper utility rather than runtime image conversion code.
