# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gximag3x.h

Internal API for Ghostscript ImageType 3x processing.

Key contents:
- Includes ImageType 3x public parameter definitions and generic image enumerator interfaces.
- Defines `IMAGE3X_MAKE_MID_PROC`, the callback signature for creating opacity/shape mask image devices at a requested width, height, and depth.
- Defines `IMAGE3X_MAKE_MCDE_PROC`, the callback signature for creating a mask-compositing/clip device and the pixel image enumerator, with both mask devices/enumerators and origins passed in.
- Exports `gx_begin_image3x_generic`, allowing renderers and high-level output writers to reuse ImageType 3x splitting while supplying custom mask handling.

Notable dependencies:
- `gsipar3x.h` for `gs_image3x_t` and mask parameter structures.
- `gxiparam.h` for image type/enumerator interfaces.

Research notes:
- This mirrors the ImageType 3 internal API but generalizes it for two masks and arbitrary mask bit depth.
- It is rendering/output infrastructure, not filesystem logic.
