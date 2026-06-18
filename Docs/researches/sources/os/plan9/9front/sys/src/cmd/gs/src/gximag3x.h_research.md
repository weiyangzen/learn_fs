# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gximag3x.h

Internal API for Ghostscript ImageType 3x processing.

Key contents:
- Includes ImageType 3x parameter definitions and generic image implementation declarations.
- Defines callback signatures for creating mask image devices and mask clipping devices/enumerators.
- Exports `gx_begin_image3x_generic`, which lets clients reuse the ImageType 3x splitting/orchestration logic while supplying custom mask-device and mask-compositing setup.

Notable dependencies:
- `gsipar3x.h` for ImageType 3x public parameter structures.
- `gxiparam.h` for image enumerator and typed image interfaces.

Research notes:
- This mirrors `gximage3.h` but expands the mask device callback for mask depth and two-mask arrays.
- The header is renderer/writer infrastructure, not filesystem code.
