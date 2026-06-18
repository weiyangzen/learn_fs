# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsiparam.h

Central public image parameter definitions.

Defines:
- `gs_image_common_t`: type pointer and `ImageMatrix`.
- Maximum image color components and planes.
- `gs_data_image_t`: width, height, bits per component, decode array, interpolate flag.
- `gs_image_format_t`: chunky, component planar, and bit planar formats.
- `gs_pixel_image_t`: data image plus format, color space, and `CombineWithColor`.
- `gs_image_alpha_t`: alpha placement options.
- `gs_image1_t` / `gs_image_t`: ImageType 1 image or image mask with `ImageMask`, `adjust`, and `Alpha`.

Exports initialization helpers:
- `gs_image_common_t_init`
- `gs_data_image_t_init`
- `gs_pixel_image_t_init`
- `gs_image_t_init_adjust`
- `gs_image_t_init_mask_adjust`
- convenience macros for default adjust behavior

Important notes:
- `gs_image_t` predates other ImageTypes, so generic image handling uses `gs_image_common_t` plus per-type structs instead of changing the old type.
- Clients must initialize image structures with helper routines because structures may grow.
- The trailing service section is disabled with `#if 0` and marked under construction.
