# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsiparam.h

## Role

`gsiparam.h` defines Ghostscript's common image parameter structures for abstract images, data images, pixel images, and ImageType 1 images/masks.

This is image parameter API infrastructure, not filesystem code.

## Main Types And Constants

- `gs_image_common_t`: image type pointer and `ImageMatrix`.
- `GS_IMAGE_MAX_COLOR_COMPONENTS`, `GS_IMAGE_MAX_COMPONENTS`, `GS_IMAGE_MAX_PLANES` plus backward-compatible aliases.
- `gs_data_image_t`: width, height, bits per component, decode array, interpolate flag.
- `gs_image_format_t`: chunky, component-planar, and bit-planar formats.
- `gs_pixel_image_t`: data image fields plus format, color space, and `CombineWithColor`.
- `gs_image_alpha_t`: no alpha, alpha first, alpha last.
- `gs_image1_t`/`gs_image_t`: ImageType 1 pixel image or mask, including `ImageMask`, mask adjustment, and alpha.
- Initialization APIs: `gs_image_common_t_init`, `gs_data_image_t_init`, `gs_pixel_image_t_init`, `gs_image_t_init_adjust`, `gs_image_t_init_mask_adjust` and compatibility macros.

## Important Contract

Clients must initialize image parameter structs with the provided initializer functions before setting fields, because the structs may grow. DataSource and MultipleDataSources are deliberately not stored in these structs.

## Notable Risks

The file includes an under-construction disabled service block. The mask initializer defaults `adjust` to true for backward compatibility, and comments call this a bad decision that cannot be changed without breaking clients.
