# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gximage3.c

Ghostscript ImageType 3 implementation for images with an explicit 1-bit mask and pixel data.

Key behavior:
- Defines `gs_image_type_3` and the ImageType 3 enumerator procedure table.
- Initializes ImageType 3 objects with color space, interleave type, and default mask dictionary decode.
- Implements the default path by rendering the mask into a monochrome memory device, then wrapping the target in a mask clipping device for pixel rendering.
- `gx_begin_image3_generic` validates mask/data geometry, interleave mode, image matrices, and optional subrectangles; creates mask and pixel image descriptors; starts nested mask/pixel image enumerators; and exposes combined plane metadata.
- Supports chunky, scan-line, and separate-source interleaving.
- `gx_image3_plane_data` splits chunky data, alternates scan-line data based on proportional mask/pixel progress, processes mask rows first, flushes masks before pixels, and tracks rows used across interruptions.
- `gx_image3_planes_wanted` indicates whether mask or pixel planes should be supplied next, including dynamic width/depth changes for scan-line interleaving.
- `gx_image3_end_image` ends nested enumerators, closes/frees the mask clip and mask memory devices, and frees row buffers.

Notable dependencies:
- Internal API from `gximage3.h`.
- Mask clipping from `gxclipm.h`.
- Memory devices from `gxdevmem.h`.
- Image state from `gxistate.h`.

Research notes:
- The implementation builds masks incrementally row by row, so flush order matters: mask rows must reach the mask device before corresponding pixel rows render.
- Chunky splitting uses simple sample load/store loops and is explicitly not optimized.
