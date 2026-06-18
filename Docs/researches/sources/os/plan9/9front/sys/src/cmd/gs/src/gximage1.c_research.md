# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gximage1.c

Ghostscript ImageType 1 initialization and serialization.

Key behavior:
- Defines separate `gx_image_type_t` records for ordinary ImageType 1 images and ImageMask images, both using `gx_begin_image1`.
- Initializes `gs_image_t` values with color space, mask flag, adjustment flag, and alpha.
- `gx_begin_image1` allocates the shared image enumerator, sets mask/alpha/adjust fields, and delegates to `gx_image_enum_begin`.
- Serializes ordinary images through generic pixel image serialization with alpha as extra control bits.
- Serializes image masks with a compact control word containing matrix presence, decode inversion, interpolation, adjustment, alpha, and bits per component.
- Releases ordinary ImageType 1 objects via generic pixel image release; mask image type uses default release because masks do not own a color space.

Notable dependencies:
- Shared image pipeline from `gximage.h`.
- Image type/procedure declarations from `gxiparam.h`.
- Stream helpers from `stream.h`.

Research notes:
- The image-mask encoding allows non-1-bit mask component depth for soft masks, even though ordinary image masks are constrained later by renderer setup.
