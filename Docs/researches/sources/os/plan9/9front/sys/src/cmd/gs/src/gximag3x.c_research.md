# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gximag3x.c

Ghostscript ImageType 3x implementation, an extension of ImageType 3-style masked images with two optional masks: opacity and shape. The file explicitly notes that the real work is not fully implemented; the default soft-mask clip path is mostly a structural wrapper that ignores the soft mask.

Key behavior:
- Defines `gs_image_type_3x` and the ImageType 3x enumerator procedure table.
- Initializes `gs_image3x_t` and its opacity/shape mask dictionaries.
- `gx_begin_image3x_generic` validates masks, computes mask/data rectangles and transforms, allocates an enumerator, creates intermediate mask devices, starts mask image enumerators, then starts the pixel image through a caller-provided mask clip/device setup callback.
- Supports omitted masks, chunky interleaved masks, and separate-source masks. Scan-line interleaving is rejected.
- `check_image3x_mask` validates mask geometry, bit depth, matrix compatibility, and allocates per-row buffers for chunky masks.
- `gx_image3x_plane_data` splits chunky data into mask and pixel buffers, feeds mask images first, flushes masks before pixel rows, and tracks row usage carefully for resumable error paths.
- `gx_image3x_planes_wanted` coordinates requested planes so opacity, shape, and pixel data stay in proportional row order.
- `gx_image3x_end_image` ends nested mask/pixel enumerators, closes intermediate devices, and frees buffers/devices/enumerator state.

Notable dependencies:
- Image definitions from `gximag3x.h` / `gsipar3x.h`.
- Memory devices from `gxdevmem.h`.
- Image state and CTM helpers from `gxistate.h`.
- `gdevbbox.h` for the default forwarding device used by the placeholder soft-mask implementation.
- Sample packing helpers from the image/sample subsystem.

Research notes:
- The default `make_mcdex_default` says there is no soft-mask analogue of the normal mask clip setup and simply forwards through a bbox device; this means ImageType 3x soft-mask behavior is incomplete in the default renderer.
- There are comments noting color-space lifetime gaps for allocated DevicePixel color spaces.
- Error cleanup is partially centralized, but a few early returns inside mask setup occur after allocation and before the normal cleanup labels, so this legacy code needs care if modified.
