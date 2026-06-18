# File Research: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngtrans.c

This file implements libpng 1.2.8 row transformation setup and shared read/write row transformation helpers. It toggles transformation flags on `png_struct` and performs in-place byte/pixel rearrangements for rows. It is not filesystem code.

Major responsibilities:
- Transformation setup APIs: `png_set_bgr`, `png_set_swap`, `png_set_packing`, `png_set_packswap`, `png_set_shift`, `png_set_interlace_handling`, `png_set_filler`, `png_set_add_alpha`, `png_set_swap_alpha`, `png_set_invert_alpha`, and `png_set_invert_mono`.
- Row transformation helpers: `png_do_invert`, `png_do_swap`, `png_do_packswap`, `png_do_strip_filler`, and `png_do_bgr`.
- User transform metadata helpers: `png_set_user_transform_info` and `png_get_user_transform_ptr`.

Control flow and data flow:
- Setup APIs primarily OR transformation bits into `png_ptr->transformations` and update related fields such as `usr_bit_depth`, `usr_channels`, `shift`, `filler`, and filler-location flags.
- `png_set_interlace_handling` marks interlace processing and returns `7` passes for interlaced images, otherwise `1`.
- `png_do_invert` inverts grayscale samples for grayscale and grayscale-alpha rows.
- `png_do_swap` swaps bytes in 16-bit samples.
- `png_do_packswap` uses static lookup tables for 1-, 2-, and 4-bit packed pixel order reversal.
- `png_do_strip_filler` removes filler or alpha bytes from RGB/RGBA and grayscale/gray-alpha rows and updates `row_info` channels, pixel depth, rowbytes, and alpha color-type bit.
- `png_do_bgr` swaps red and blue channels for 8-bit and 16-bit RGB/RGBA rows.
- User transform info is stored only when `PNG_USER_TRANSFORM_PTR_SUPPORTED` is compiled in.

Notable implementation details:
- Transform support is heavily compile-time gated.
- Packed-pixel swapping is table-driven for speed and simplicity.
- `png_do_strip_filler` handles before/after filler layouts and both 8-bit and 16-bit samples.
- Functions mutate row buffers in place and must be called in the correct transform order by read/write pipelines elsewhere.
- Some NULL checks are compiled only with `PNG_USELESS_TESTS_SUPPORTED`.

Important dependencies:
- `png_struct`, `png_row_info`, transformation flags, color constants, and feature macros from `png.h`.
- Called by read/write transform pipelines outside this file.

Research notes:
- This is a low-level image row manipulation module.
- It has no direct storage or filesystem responsibilities.
- Audit attention should focus on in-place buffer assumptions, rowbytes/channel updates, and correctness across bit-depth/color-type combinations.
