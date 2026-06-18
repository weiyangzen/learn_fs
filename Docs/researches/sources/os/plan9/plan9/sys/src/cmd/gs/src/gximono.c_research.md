# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gximono.c

General mono-component image renderer for Ghostscript.

Key behavior:
- Provides image class strategy `gs_image_class_3_mono`, selected for one-sample-per-pixel images.
- Chooses slower loops for imagemasks with halftone colors or non-default RasterOps; otherwise it can bypass X clipping for portrait mono images.
- Precomputes fixed-point DDA values and scales ImageType 4 mask-color ranges to byte sample space.
- `image_render_mono` handles single scanlines for DeviceGray, DevicePixel, CIEBasedA, Separation, Indexed-style inputs, and imagemasks.
- Uses cached device-color clues so repeated sample values avoid repeated remapping.
- Has slow paths for masked/non-masked portrait, landscape, and skewed images using `fill_parallelogram`.
- Has a fast portrait path using run detection and rectangle/RasterOp fills.
- Saves source offset in `penum->used` on error so rendering can resume.

Notable dependencies:
- Image state from `gximage.h`.
- Color mapping/device color helpers from `gxcmap.h`, `gxdcolor.h`, and `gxistate.h`.
- Halftone/cache support from `gzht.h`.
- Fixed-point/DDA helpers from `gxmatrix.h`, `gxarith.h`, and `gxfixed.h`.

Research notes:
- This is performance-sensitive legacy raster code with manually optimized run skipping.
- A comment notes the slow orthogonal non-mask path does not apply adjustment.
