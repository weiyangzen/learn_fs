# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jquant2.c

Purpose: two-pass color quantizer using Heckbert-style median cut to build an image-specific colormap, then map pixels to that map with optional Floyd-Steinberg dithering.

Key contents:
- Compiled only when `QUANT_2PASS_SUPPORTED` is enabled.
- RGB distance scale factors: `R_SCALE = 2`, `G_SCALE = 3`, `B_SCALE = 1`.
- Histogram precision: 5 bits for C0, 6 bits for C1, 5 bits for C2.
- `my_cquantizer` stores public methods, saved colormap, desired color count, histogram/inverse-cache storage, zeroing flag, F-S workspace, and error limiter.
- `prescan_quantize()` accumulates the reduced-precision histogram.
- Median-cut machinery: `box`, `find_biggest_color_pop()`, `find_biggest_volume()`, `update_box()`, `median_cut()`, `compute_color()`, `select_colors()`.
- Inverse colormap cache machinery: `find_nearby_colors()`, `find_best_colors()`, `fill_inverse_cmap()`.
- Mapping routines: `pass2_no_dither()` and `pass2_fs_dither()`.
- Error limiting: `init_error_limit()`.
- Pass lifecycle: `start_pass_2_quant()`, `finish_pass1()`, `finish_pass2()`, `new_color_map_2_quant()`.
- Public init entry: `jinit_2pass_quantizer()`.

Important behavior:
- Only supports three output color components; other cases call `JERR_NOTIMPL`.
- First pass records histogram cells, clamping 16-bit cell overflow.
- Color selection starts from one box covering the color cube, shrinks boxes to nonempty cells, splits by population first and by volume later, then uses pixel-weighted means for representative colors.
- Reuses histogram storage during pass 2 as a lazy inverse colormap cache; zero means uncached, stored values are colormap index plus one.
- Nearest-color searches fill small update boxes rather than the full histogram, using locality filtering and incremental distance computation.
- Ordered dithering is not supported; any non-none dither mode becomes Floyd-Steinberg.
- Floyd-Steinberg path limits applied error through a transfer table to reduce visual artifacts.
- `new_color_map_2_quant()` marks the inverse cache for zeroing before reuse.

Dependencies:
- `jinclude.h`, `jpeglib.h`, IJG memory manager, `jzero_far()`, sample range-limit table, error/trace macros.
