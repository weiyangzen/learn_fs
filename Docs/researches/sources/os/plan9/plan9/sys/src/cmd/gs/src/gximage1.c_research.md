# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gximage1.c

Ghostscript ImageType 1 initialization and serialization.

Key behavior:
- Defines separate `gx_image_type_t` records for ordinary ImageType 1 images and ImageMask images.
- Initializes `gs_image_t` with color space, ImageMask flag, adjustment flag, type pointer, and alpha.
- `gx_begin_image1` allocates the shared image enumerator, sets alpha/mask/adjust fields, and delegates to `gx_image_enum_begin`.
- Serializes ordinary images through generic pixel image serialization, using the extra control bits for alpha.
- Serializes image masks with a compact mask-specific control word containing matrix presence, decode inversion, interpolation, adjustment, alpha, and bits/component.
- Releases ordinary ImageType 1 pixel image objects through `gx_pixel_image_release`; mask images use default release because they do not own a color space.

Notable dependencies:
- Shared image pipeline from `gximage.h`.
- Image type/enumerator declarations from `gxiparam.h`.
- Stream helpers from `stream.h`.

Research notes:
- ImageMask serialization carries bits/component for soft masks even though normal imagemasks are later constrained by renderer setup.
