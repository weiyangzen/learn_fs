# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/readyuv.c

Reader for Abekas A66-style raw YUV images. Like `readv210.c`, it relies on `/lib/video.specs` and file length to infer pixels, lines, and whether the source stores 8-bit or 10-bit samples.

It reads the high 8 bits of every multiplexed YUV sample first, then optionally reads packed low 2-bit planes for 10-bit input. Samples are converted from YCbCr pairs to planar 8-bit RGB channels using fixed-point coefficients.

The public API is `Breadyuv`/`readyuv`; it accepts `CYCbCr` as the requested color space and returns a `Rawimage` marked `CRGB`.
