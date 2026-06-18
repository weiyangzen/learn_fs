# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gximono.c

General mono-component image renderer for Ghostscript.

Key behavior:
- Provides image class strategy `gs_image_class_3_mono`, selected when an image has one sample per pixel.
- Chooses slow loops for image masks with halftone colors or non-default RasterOps, and otherwise can bypass some X clipping for portrait mono images.
- Precomputes DDA/fixed-point state and mask-color scaling.
- `image_render_mono` renders one scanline for single-component DeviceGray/DevicePixel/CIE/Separation/Indexed-style inputs and masks.
- Uses cached device-color “clues” so repeated sample values avoid repeated color remapping.
- Implements slow paths for masked/non-masked, portrait/landscape/skewed cases using `fill_parallelogram`.
- Implements a fast portrait path using run detection and `fill_rectangle` / device RasterOp rectangle fills.
- Saves source offset on error so image processing can resume.

Notable dependencies:
- Image state from `gximage.h`.
- Color mapping and device color helpers from `gxcmap.h`, `gxdcolor.h`, and `gxistate.h`.
- Halftone/cache state from `gzht.h`.

Research notes:
- This is performance-sensitive legacy raster code with hand-unrolled run skipping for common mono cases.
- Some comments call out limitations, such as missing adjustment in one slow orthogonal non-mask path.
