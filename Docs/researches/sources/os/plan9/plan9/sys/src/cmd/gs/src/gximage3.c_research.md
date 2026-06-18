# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gximage3.c

Ghostscript ImageType 3 implementation for images with an explicit 1-bit mask plus pixel data.

Key behavior:
- Defines `gs_image_type_3` and the ImageType 3 enumerator procedure table.
- Initializes ImageType 3 images with color space, interleave type, and default inverted mask decode.
- Default rendering creates a monochrome memory device for the mask and a mask clipping device in front of the target for pixel rendering.
- `gx_begin_image3_generic` validates mask/data dimensions, interleave modes, matrix compatibility, optional subrectangles, and starts nested mask/pixel ImageType 1 enumerators.
- Supports chunky interleaving, scan-line interleaving, and separate-source interleaving.
- `gx_image3_plane_data` splits chunky data, alternates scan-line data, processes mask rows before pixel rows, flushes mask data before pixel drawing, and preserves resumability with `mask_skip`.
- `gx_image3_planes_wanted` reports current plane needs and updates width/depth for scan-line interleave.
- `gx_image3_end_image` ends nested enumerators, closes mask clip and mask memory devices, and frees row buffers/state.

Notable dependencies:
- Internal API from `gximage3.h`.
- Mask clipping from `gxclipm.h`.
- Memory devices from `gxdevmem.h`.
- Image state and CTM helpers from `gxistate.h`.

Research notes:
- The mask is built incrementally row by row, so mask flushing order is essential before corresponding pixels are rendered.
- Chunky sample splitting is intentionally simple and not optimized.
- There is an Alpha/gcc padding workaround when copying `gs_pixel_image_t` into `gs_image_t`.
