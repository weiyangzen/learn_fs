# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gximage.h

Internal image rendering state header for Ghostscript’s default image pipeline.

Key contents:
- Defines `sample_map`, decode modes, and macros for decoding byte or frac samples into client colors.
- Declares optional external 12-bit and 16-bit sample unpack procedure pointers.
- Defines `image_posture` for portrait, landscape, and skewed image transforms.
- Defines `gx_image_clue`, a cached device-color lookup entry.
- Defines the large `gx_image_enum` structure used by ImageType 1 and 4 rendering, including source format, mask/alpha state, matrix/posture, clip flags, RasterOp state, DDA state, buffers, sample maps, scaler state, and 256 color clues.
- Declares GC pointer enumeration macros and core initialization APIs: `gx_image_enum_alloc`, `gx_image_enum_begin`, `image_init_clues`, and `gx_image_scale_mask_colors`.

Notable dependencies:
- Public image parameters from `gsiparam.h`.
- Color-space and sample helpers from `gxcspace.h` and `gxsample.h`.
- Interpolation stream state via `strimpl.h` and `sisparam.h`.
- Image class interfaces from `gxiclass.h`.

Research notes:
- The header exposes implementation state because image class strategy functions and renderers operate directly on `gx_image_enum`.
- The clue cache is a performance feature for mono/color image rendering, avoiding repeated color remapping for recurring sample values.
