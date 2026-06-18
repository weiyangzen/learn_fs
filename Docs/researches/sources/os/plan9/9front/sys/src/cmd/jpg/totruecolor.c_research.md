# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/totruecolor.c

Rawimage converter from the project’s decoded formats to true-color or grayscale packed formats. Target descriptors are `CY`, `CRGB24`, and `CRGBA32`.

It handles grayscale, indexed `CRGB1`/`CRGBV`, planar `CRGB`/`CRGBA`, and planar `CYCbCr`. Indexed colors are expanded from color maps; YCbCr is converted with fixed-point coefficients; RGBA output premultiplies alpha.

This is a central bridge between format decoders that produce planar or indexed `Rawimage` data and display/writer code expecting packed Plan 9 channels.
