# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gximag3x.c

Ghostscript ImageType 3x implementation, extending ImageType 3-style masked images with separate optional opacity and shape masks. The file explicitly says the real soft-mask work is not yet implemented; the default path mostly orchestrates data splitting and forwards pixel rendering through a bbox device.

Key behavior:
- Defines `gs_image_type_3x`, ImageType 3x enumerator procs, and initialization for `gs_image3x_t` plus opacity/shape mask dictionaries.
- `gx_begin_image3x_generic` validates mask geometry, interleave modes, matrix compatibility, allocates the combined enumerator, creates mask devices, starts nested mask image enumerators, and starts the pixel image through a caller-supplied mask-compositing callback.
- Supports omitted masks, chunky masks interleaved with pixel samples, and separate-source masks; scan-line interleaving is rejected.
- `check_image3x_mask` validates mask dimensions/depths and computes proportional subrectangles for masks.
- `gx_image3x_plane_data` splits chunky mask/pixel rows, feeds masks before pixel rows, flushes mask enumerators before pixel rendering, and tracks row usage/skips for resumable error paths.
- `gx_image3x_planes_wanted` coordinates opacity, shape, and pixel planes so earlier channels stay at least as far progressed as later channels.
- `gx_image3x_end_image` ends nested enumerators, closes devices, and frees row buffers/devices/enumerator state.

Notable dependencies:
- ImageType 3x declarations from `gximag3x.h` and public parameters from `gsipar3x.h`.
- Memory/image devices from `gxdevmem.h`.
- Image state helpers from `gxistate.h`.
- `gdevbbox.h` for the default forwarding device used by the placeholder soft-mask path.
- Sample load/store macros from Ghostscript’s sample subsystem.

Research notes:
- The default `make_mcdex_default` says there is no soft-mask analogue of ImageType 3 mask clipping and simply ignores the soft mask while forwarding through a bbox device.
- The file allocates DevicePixel color spaces for mask rendering and has an inline comment noting missing color-space lifetime cleanup on error/end paths.
- Several early returns in mask setup happen after allocation, so cleanup/error maintenance is delicate.
