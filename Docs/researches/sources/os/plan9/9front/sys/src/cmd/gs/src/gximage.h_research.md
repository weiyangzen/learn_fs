# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gximage.h

Internal image rendering state header for Ghostscript’s default image pipeline.

Key contents:
- Defines `sample_map`, sample decoding modes, decode macros, and declarations for optional 12-bit/16-bit sample unpacking procedures.
- Defines `image_posture` for portrait, landscape, and skewed image transforms.
- Defines color lookup “clue” entries used to cache mapped device colors.
- Defines the large `gx_image_enum` state object used by ImageType 1 and 4 rendering, including image format, alpha/mask state, matrix/posture, clipping, RasterOp state, buffers, scaling state, DDA state, decode maps, and color clues.
- Declares GC pointer enumeration macros for `gx_image_enum`.
- Declares shared initialization APIs: `gx_image_enum_alloc`, `gx_image_enum_begin`, `image_init_clues`, and `gx_image_scale_mask_colors`.

Notable dependencies:
- Image parameter definitions from `gsiparam.h` and `gxiparam.h`.
- Color-space and sample helpers from `gxcspace.h` and `gxsample.h`.
- Interpolation state from stream interpolation headers.

Research notes:
- This header exposes many implementation details because image class strategy functions and renderers operate directly on `gx_image_enum`.
- The clue cache is central to mono/color image performance, avoiding repeated color remapping for repeated sample values.
