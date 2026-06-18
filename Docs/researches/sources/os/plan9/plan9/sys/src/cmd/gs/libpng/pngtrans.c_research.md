# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngtrans.c

`pngtrans.c` implements row transform configuration APIs and several shared read/write row transformation routines. It is used by both reader and writer paths to set transformation flags in `png_struct` and to mutate row buffers according to those flags.

Configuration APIs:
- `png_set_bgr` enables RGB/BGR channel swapping.
- `png_set_swap` enables 16-bit byte swapping when the image bit depth is 16.
- `png_set_packing` expands sub-8-bit samples to packed 8-bit user depth.
- `png_set_packswap` reverses packed pixel order inside bytes for 1-, 2-, or 4-bit pixels.
- `png_set_shift` records significant-bit shifting parameters.
- `png_set_interlace_handling` enables interlace handling and returns `7` passes for interlaced images or `1` otherwise.
- `png_set_filler` configures filler insertion/removal location and updates expected user channel count for RGB or grayscale inputs.
- `png_set_add_alpha` wraps `png_set_filler` and marks alpha addition.
- `png_set_swap_alpha`, `png_set_invert_alpha`, and `png_set_invert_mono` enable alpha/mono inversion or swapping flags.
- `png_set_user_transform_info` records user transform pointer/depth/channel metadata where supported.
- `png_get_user_transform_ptr` returns the user transform pointer when that feature is compiled in.

Row transformation routines:
- `png_do_invert` inverts grayscale data, including gray-alpha rows while preserving alpha bytes.
- `png_do_swap` swaps byte order for all 16-bit samples.
- `png_do_packswap` uses static 256-byte lookup tables for 1-, 2-, and 4-bit packed-pixel bit-order reversal.
- `png_do_strip_filler` removes filler or alpha bytes/words from RGB/RGBA and grayscale/gray-alpha rows, updates channels, pixel depth, rowbytes, and optionally clears the alpha color-type bit.
- `png_do_bgr` swaps red and blue components for RGB/RGBA rows at 8-bit and 16-bit depths.

Important dependencies and state:
- Includes `png.h` with `PNG_INTERNAL`.
- Operates on `png_struct` transformation flags and `png_row_info` row metadata.
- Compile-time feature macros select which transforms are available for read, write, legacy, and user-transform builds.

Edge cases and risks:
- These functions mutate row buffers in place; pointer increments and row metadata updates must stay synchronized.
- Packed-pixel transforms depend on correct `row_info->bit_depth` and `row_info->rowbytes`.
- `png_do_strip_filler` has separate first-pixel handling in filler-after 16-bit/RGB paths, so changes here can easily introduce off-by-one row corruption.
- Public configuration setters generally assume a valid `png_ptr`; unlike many metadata setters, they do not consistently null-guard.
