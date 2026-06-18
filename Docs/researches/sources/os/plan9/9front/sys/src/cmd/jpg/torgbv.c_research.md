# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/torgbv.c

Rawimage remapper to Plan 9 RGBV (`CRGBV`) indexed color. It handles indexed RGB maps, RGB/Y/CbCr planar images, packed RGB/RGBA images, and grayscale/gray-alpha inputs.

The converter uses generated `rgbv.h` and `ycbcr.h` lookup tables, optional modified Floyd-Steinberg error diffusion, and clamp/error arrays per scanline. Output is a one-channel `Rawimage` sharing the source rectangle and containing palette indices.

Failures are reported through `_remaperror`, setting `errstr` and returning `nil`.
